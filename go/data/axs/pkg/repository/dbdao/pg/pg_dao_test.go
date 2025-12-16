package pg_test

import (
	"fmt"
	"testing"
	"time"

	"github.com/google/uuid"
	pglib "github.com/lib/pq"
	"github.com/rs/zerolog"
	"github.com/shopspring/decimal"
	"github.com/stretchr/testify/suite"
	"github.com/vx416/axs/pkg/model"
	"github.com/vx416/axs/pkg/repository/dbdao/pg"
	"github.com/vx416/axs/pkg/repository/dbdao/sqlx_adapter"
	"github.com/vx416/axs/pkg/service/svcerr"
	"github.com/vx416/axs/pkg/testutil"
	"github.com/vx416/axs/pkg/testutil/factory"
	"github.com/vx416/axs/pkg/utils"
)

func TestPGDaoSuite(t *testing.T) {
	testInstance, err := testutil.NewTestInstance(t)
	if err != nil {
		t.Fatalf("failed to create test instance: %v", err)
	}
	suite.Run(t, &PGDaoSuite{
		TestInstance: testInstance,
	})

}

type PGDaoSuite struct {
	TestInstance *testutil.TestInstance
	*pg.PGDao
	suite.Suite
	DefaultLeaderLock *model.PartitionLeaderLock
}

func (suite *PGDaoSuite) SetupSuite() {
	sqlxAdapter := sqlx_adapter.NewSqlxAdapter(suite.TestInstance.SqlxDB)
	dao, err := pg.NewPGDao(sqlxAdapter, suite.TestInstance.PgxConn)
	suite.Require().NoError(err, "Failed to create PGDao")
	suite.PGDao = dao
	suite.DefaultLeaderLock = &model.PartitionLeaderLock{
		Topic:       "test",
		Partition:   1,
		LeaderSvcID: "test",
	}
	zerolog.SetGlobalLevel(zerolog.ErrorLevel)
	_, _, err = suite.PGDao.CreateAndTruncateTempTables(suite.TestInstance.Ctx, 1)
	suite.Require().NoError(err, "Failed to create temp tables")
}

func (suite *PGDaoSuite) SetupTestData() {
	err := suite.TestInstance.ResetDB()
	suite.Require().NoError(err, "failed to reset and run seed data")
	err = suite.TestInstance.PGCopyFromLargeJson()
	suite.Require().NoError(err, "failed to copy from JSON data")
	suite.acquireLeaderLock()
}

func (suite *PGDaoSuite) acquireLeaderLock() {
	lockData, ok, err := suite.PGDao.AcquirePartitionLeaderLock(suite.TestInstance.Ctx, suite.DefaultLeaderLock.Topic, suite.DefaultLeaderLock.Partition, suite.DefaultLeaderLock.LeaderSvcID)
	suite.Require().NoError(err, "Failed to acquire partition leader lock")
	suite.Require().True(ok, "Failed to acquire partition leader lock")
	suite.DefaultLeaderLock = &lockData
}

func (suite *PGDaoSuite) TestApplyLargeBalanceChanges() {
	suite.SetupTestData()

	writeBalanceAccounts, changeLogs := suite.loadTestInputData(10000)
	start := time.Now()
	err := suite.PGDao.ApplyAccountBalanceChanges(suite.TestInstance.Ctx, writeBalanceAccounts, changeLogs, suite.DefaultLeaderLock)
	suite.Require().NoError(err, "ApplyAccountBalanceChangesV2 failed")
	v2Cost := time.Since(start)
	suite.T().Logf("new ApplyAccountBalanceChanges apply 10k take %v", v2Cost)
	suite.assertApplyResults(changeLogs)

	suite.SetupTestData()
	start = time.Now()
	err = suite.PGDao.ApplyAccountBalanceChangesOLD(suite.TestInstance.Ctx, writeBalanceAccounts, changeLogs, suite.DefaultLeaderLock)
	suite.Require().NoError(err, "ApplyAccountBalanceChangesV2 failed")
	v1Cost := time.Since(start)
	suite.T().Logf("old ApplyAccountBalanceChanges apply 10k took %v", v1Cost)
	suite.Greater(v1Cost, v2Cost, "v1 should be greater than v2")
	suite.assertApplyResults(changeLogs)
}

func (suite *PGDaoSuite) TestApplyMediumBalanceChanges() {
	suite.SetupTestData()

	writeBalanceAccounts, changeLogs := suite.loadTestInputData(2000)
	start := time.Now()
	err := suite.PGDao.ApplyAccountBalanceChanges(suite.TestInstance.Ctx, writeBalanceAccounts, changeLogs, suite.DefaultLeaderLock)
	suite.Require().NoError(err, "new ApplyAccountBalanceChanges  failed")
	v2Cost := time.Since(start)
	suite.T().Logf("new ApplyAccountBalanceChanges apply 2k took %v", v2Cost)
	suite.assertApplyResults(changeLogs)

	suite.SetupTestData()
	start = time.Now()
	err = suite.PGDao.ApplyAccountBalanceChangesOLD(suite.TestInstance.Ctx, writeBalanceAccounts, changeLogs, suite.DefaultLeaderLock)
	suite.Require().NoError(err, "old ApplyAccountBalanceChanges failed")
	v1Cost := time.Since(start)
	suite.T().Logf("old ApplyAccountBalanceChanges apply 2k took %v", v1Cost)
	suite.Greater(v1Cost, v2Cost, "v1 should be greater than v2")
	suite.assertApplyResults(changeLogs)
}

func (suite *PGDaoSuite) TestApplySmallBalanceChanges() {
	suite.SetupTestData()

	writeBalanceAccounts, changeLogs := suite.loadTestInputData(300)
	start := time.Now()
	err := suite.PGDao.ApplyAccountBalanceChanges(suite.TestInstance.Ctx, writeBalanceAccounts, changeLogs, suite.DefaultLeaderLock)
	suite.Require().NoError(err, "new ApplyAccountBalanceChanges failed")
	v2Cost := time.Since(start)
	suite.T().Logf("new ApplyAccountBalanceChanges apply 300 took %v", v2Cost)
	suite.assertApplyResults(changeLogs)

	suite.SetupTestData()
	start = time.Now()
	err = suite.PGDao.ApplyAccountBalanceChangesOLD(suite.TestInstance.Ctx, writeBalanceAccounts, changeLogs, suite.DefaultLeaderLock)
	suite.Require().NoError(err, "old ApplyAccountBalanceChangesV2 failed")
	v1Cost := time.Since(start)
	suite.T().Logf("old ApplyAccountBalanceChanges apply 300 took %v", v1Cost)
	suite.Greater(v1Cost, v2Cost, "v1 should be greater than v2")
	suite.assertApplyResults(changeLogs)
}

func (suite *PGDaoSuite) loadTestInputData(size int) (map[int64]*model.WriteAccount, []*model.EventApplyResult) {
	queryChangeLogs := fmt.Sprintf(`SELECT idempotency_key, change_id, account_id, account_shard_id, user_id, currency_code, available_delta, frozen_delta FROM balance_change_logs WHERE status = 0 ORDER BY id ASC LIMIT %d;`, size)
	changeLogs := []*model.EventApplyResult{}
	writeAccount := map[int64]*model.WriteAccount{}

	rows, err := suite.TestInstance.SqlxDB.QueryContext(suite.TestInstance.Ctx, queryChangeLogs)
	suite.Require().NoError(err, "Failed to query change logs")
	for rows.Next() {
		var idempotencyKey string
		var changeID int64
		var accountID int64
		var shardID int32
		var userID int64
		var currencyCode string
		var availableDelta decimal.Decimal
		var frozenDelta decimal.Decimal

		err := rows.Scan(&idempotencyKey, &changeID, &accountID, &shardID, &userID, &currencyCode, &availableDelta, &frozenDelta)
		suite.Require().NoError(err, "Failed to scan change log row")
		changeLog := &model.EventApplyResult{
			IdempotencyKey: idempotencyKey,
			ChangeID:       changeID,
			AccountID:      accountID,
			ShardID:        shardID,
			Status:         model.ChangeLogStatusApplied,
		}
		changeLogs = append(changeLogs, changeLog)
		if _, exists := writeAccount[accountID]; !exists {
			writeAccount[accountID] = model.NewWriteAccount(accountID, userID, shardID)
		}
		writeAccount[accountID].ApplyChange(model.CurrencyCode(currencyCode), availableDelta, frozenDelta, false)
	}
	return writeAccount, changeLogs
}

func (suite *PGDaoSuite) assertApplyResults(changeLogs []*model.EventApplyResult) {
	verifyQuery := `
		WITH agg AS (
		    SELECT 
		        user_id,
		        currency_code,
		        SUM(available_delta) AS sum_available,
		        SUM(frozen_delta) AS sum_frozen
		    FROM balance_change_logs
		    WHERE status = 1
		    GROUP BY user_id, currency_code
		)
		SELECT 
		    COUNT(1)
		FROM account_balances ab
		LEFT JOIN agg 
		    ON ab.user_id = agg.user_id
		   AND ab.currency_code = agg.currency_code
		WHERE 
		      ab.available <> COALESCE(agg.sum_available, 0)
		   OR ab.frozen    <> COALESCE(agg.sum_frozen, 0);`
	var mismatchCount int
	err := suite.TestInstance.SqlxDB.QueryRowContext(suite.TestInstance.Ctx, verifyQuery).Scan(&mismatchCount)
	suite.Require().NoError(err, "Failed to verify apply results")
	suite.Equal(0, mismatchCount, "There are %d mismatched account balances after applying changes", mismatchCount)

	idemKeys := []string{}
	for _, log := range changeLogs {
		idemKeys = append(idemKeys, log.IdempotencyKey)
	}
	idemStatus, err := suite.PGDao.GetIdempotencyKeysStatus(suite.TestInstance.Ctx, idemKeys, 0)
	suite.Require().NoError(err, "Failed to get idempotency keys status")
	for _, log := range changeLogs {
		status, exists := idemStatus[log.IdempotencyKey]
		suite.Require().True(exists, "Idempotency key %s not found in DB", log.IdempotencyKey)
		suite.Equal(model.ChangeLogStatusApplied, status, "Idempotency key %s has incorrect status", log.IdempotencyKey)
	}
}

func (suite *PGDaoSuite) TestApplyNotExistAccountBalance() {
	uid := 99999
	err := suite.TestInstance.ResetDB()
	suite.acquireLeaderLock()
	suite.Require().NoError(err, "failed to reset and run seed data")
	writeBalanceAccounts := factory.WriteAccount.BuildSeqUserID(uid, uid, 1, []string{"BTC"}, []int{100, 100}, []int{100, 100})
	changeLogs := suite.insertMockChangeLog(writeBalanceAccounts)
	err = suite.PGDao.ApplyAccountBalanceChanges(suite.TestInstance.Ctx, writeBalanceAccounts, changeLogs, suite.DefaultLeaderLock)
	suite.Require().NoError(err, "ApplyAccountBalanceChangesV2 failed")
	suite.assertApplyResults(changeLogs)

	opt := model.ListAccountBalancesOptions{}
	opt.AddFilter(int64(uid), "BTC", 1)
	balance, err := suite.PGDao.ListAccountBalances(suite.TestInstance.Ctx, opt)
	suite.Require().NoError(err, "ListAccountBalances failed")
	suite.Require().Len(balance, 1, "Expected 1 account balance record")
	available, _ := balance[int64(uid)].GetAvailableAmount(model.CurrencyCode("BTC"))
	frozen, _ := balance[int64(uid)].GetAvailableAmount(model.CurrencyCode("BTC"))
	suite.EqualValues(decimal.NewFromInt(100).String(), available.String(), "Available balance mismatch")
	suite.EqualValues(decimal.NewFromInt(100).String(), frozen.String(), "Frozen balance mismatch")
}

func (suite *PGDaoSuite) TestApplyFailedInsufficientBalance() {
	err := suite.TestInstance.ResetDB()
	suite.Require().NoError(err, "failed to reset and run seed data")
	suite.acquireLeaderLock()

	uid := 99999
	suite.Require().NoError(err, "failed to reset and run seed data")
	writeBalanceAccounts := factory.WriteAccount.BuildSeqUserID(uid, uid, 1, []string{"BTC"}, []int{-100, -100}, []int{-100, -100})
	changeLogs := suite.insertMockChangeLog(writeBalanceAccounts)
	err = suite.PGDao.ApplyAccountBalanceChanges(suite.TestInstance.Ctx, writeBalanceAccounts, changeLogs, suite.DefaultLeaderLock)
	suite.Require().True(utils.ErrIs(err, svcerr.ErrBalanceInsufficient))

	err = suite.TestInstance.ResetDB()
	suite.Require().NoError(err, "failed to reset and run seed data")
	suite.acquireLeaderLock()
	err = suite.TestInstance.ResetAndRunSeedData()
	suite.Require().NoError(err, "failed to reset and run seed data")

	opt := model.ListAccountBalancesOptions{}
	opt.AddFilter(1, "BTC", 1)
	opt.AddFilter(1, "ETH", 1)
	opt.AddFilter(2, "BTC", 1)
	opt.AddFilter(2, "ETH", 1)
	beforeAccounts, err := suite.PGDao.ListAccountBalances(suite.TestInstance.Ctx, opt)
	suite.Require().NoError(err, "ListAccountBalances failed")

	acc1 := factory.WriteAccount.WithAccInfo(1, 1, 1, []string{"BTC", "ETH"}, []int{-99999999, -99999999}, []int{0, 0}).MustBuild().(*model.WriteAccount)
	acc2 := factory.WriteAccount.WithAccInfo(2, 1, 2, []string{"BTC", "ETH"}, []int{9999999, 9999999}, []int{0, 0}).MustBuild().(*model.WriteAccount)
	writeBalanceAccounts2 := map[int64]*model.WriteAccount{
		acc1.AccountID: acc1, acc2.AccountID: acc2,
	}
	changeLogs2 := suite.insertMockChangeLog(writeBalanceAccounts2)
	err = suite.PGDao.ApplyAccountBalanceChanges(suite.TestInstance.Ctx, writeBalanceAccounts2, changeLogs2, suite.DefaultLeaderLock)
	suite.Require().True(utils.ErrIs(err, svcerr.ErrBalanceInsufficient))

	afterAccounts, err := suite.PGDao.ListAccountBalances(suite.TestInstance.Ctx, opt)
	suite.Require().NoError(err, "ListAccountBalances failed")
	for _, beforeAcc := range beforeAccounts {
		afterAcc := afterAccounts[beforeAcc.AccountID]
		for _, beforeBalance := range beforeAcc.AccountBalancesMap {
			afterAvailable, _ := afterAcc.GetAvailableAmount(beforeBalance.CurrencyCode)
			afterFrozen, _ := afterAcc.GetFrozenAmount(beforeBalance.CurrencyCode)
			suite.Require().True(beforeBalance.Available.Equal(afterAvailable))
			suite.Require().True(beforeBalance.Frozen.Equal(afterFrozen))
		}
	}
}

func (suite *PGDaoSuite) TestApplyFailedIdempotencyViolation() {
	err := suite.TestInstance.ResetDB()
	suite.Require().NoError(err, "failed to reset and run seed data")
	err = suite.TestInstance.ResetAndRunSeedData()
	suite.Require().NoError(err, "failed to reset and run seed data")
	suite.acquireLeaderLock()

	opt := model.ListAccountBalancesOptions{}
	opt.AddFilter(1, "BTC", 1)
	opt.AddFilter(1, "ETH", 1)
	opt.AddFilter(2, "BTC", 1)
	opt.AddFilter(2, "ETH", 1)
	beforeAccounts, err := suite.PGDao.ListAccountBalances(suite.TestInstance.Ctx, opt)
	suite.Require().NoError(err, "ListAccountBalances failed")

	acc1 := factory.WriteAccount.WithAccInfo(1, 1, 1, []string{"BTC", "ETH"}, []int{99999999, 99999999}, []int{0, 0}).MustBuild().(*model.WriteAccount)
	acc2 := factory.WriteAccount.WithAccInfo(2, 1, 2, []string{"BTC", "ETH"}, []int{9999999, 9999999}, []int{0, 0}).MustBuild().(*model.WriteAccount)
	writeBalanceAccounts2 := map[int64]*model.WriteAccount{
		acc1.AccountID: acc1, acc2.AccountID: acc2,
	}
	changeLogs2 := suite.insertMockChangeLog(writeBalanceAccounts2)

	err = suite.PGDao.BatchUpdateChangeLogStatus(suite.TestInstance.Ctx, changeLogs2)
	suite.Require().NoError(err, "BatchUpdateChangeLogStatus failed")

	err = suite.PGDao.ApplyAccountBalanceChanges(suite.TestInstance.Ctx, writeBalanceAccounts2, changeLogs2, suite.DefaultLeaderLock)
	suite.Require().True(utils.ErrIs(err, svcerr.ErrIdempotentViolation), "Expected ErrIdempotentViolation, got %v", err)

	afterAccounts, err := suite.PGDao.ListAccountBalances(suite.TestInstance.Ctx, opt)
	suite.Require().NoError(err, "ListAccountBalances failed")
	for _, beforeAcc := range beforeAccounts {
		afterAcc := afterAccounts[beforeAcc.AccountID]
		for _, beforeBalance := range beforeAcc.AccountBalancesMap {
			afterAvailable, _ := afterAcc.GetAvailableAmount(beforeBalance.CurrencyCode)
			afterFrozen, _ := afterAcc.GetFrozenAmount(beforeBalance.CurrencyCode)
			suite.Require().True(beforeBalance.Available.Equal(afterAvailable))
			suite.Require().True(beforeBalance.Frozen.Equal(afterFrozen))
		}
	}
}

func (suite *PGDaoSuite) TestApplyFailedLeadershipChange() {
	err := suite.TestInstance.ResetDB()
	suite.Require().NoError(err, "failed to reset and run seed data")
	err = suite.TestInstance.ResetAndRunSeedData()
	suite.Require().NoError(err, "failed to reset and run seed data")
	suite.acquireLeaderLock()

	opt := model.ListAccountBalancesOptions{}
	opt.AddFilter(1, "BTC", 1)
	opt.AddFilter(1, "ETH", 1)
	opt.AddFilter(2, "BTC", 1)
	opt.AddFilter(2, "ETH", 1)
	beforeAccounts, err := suite.PGDao.ListAccountBalances(suite.TestInstance.Ctx, opt)
	suite.Require().NoError(err, "ListAccountBalances failed")

	_, err = suite.TestInstance.SqlxDB.ExecContext(suite.TestInstance.Ctx, `UPDATE `+pg.PartitionLeaderLocksTable+` SET leader_svc_id = 'another_service' WHERE topic = $1 AND partition = $2;`, suite.DefaultLeaderLock.Topic, suite.DefaultLeaderLock.Partition)
	suite.Require().NoError(err, "Failed to change partition leader lock owner")

	acc1 := factory.WriteAccount.WithAccInfo(1, 1, 1, []string{"BTC", "ETH"}, []int{99999999, 99999999}, []int{0, 0}).MustBuild().(*model.WriteAccount)
	acc2 := factory.WriteAccount.WithAccInfo(2, 1, 2, []string{"BTC", "ETH"}, []int{9999999, 9999999}, []int{0, 0}).MustBuild().(*model.WriteAccount)
	writeBalanceAccounts2 := map[int64]*model.WriteAccount{
		acc1.AccountID: acc1, acc2.AccountID: acc2,
	}
	changeLogs2 := suite.insertMockChangeLog(writeBalanceAccounts2)

	err = suite.PGDao.ApplyAccountBalanceChanges(suite.TestInstance.Ctx, writeBalanceAccounts2, changeLogs2, suite.DefaultLeaderLock)
	suite.Require().True(utils.ErrIs(err, svcerr.ErrLeaderChange), "Expected ErrLeaderChange, got %v", err)

	afterAccounts, err := suite.PGDao.ListAccountBalances(suite.TestInstance.Ctx, opt)
	suite.Require().NoError(err, "ListAccountBalances failed")
	for _, beforeAcc := range beforeAccounts {
		afterAcc := afterAccounts[beforeAcc.AccountID]
		for _, beforeBalance := range beforeAcc.AccountBalancesMap {
			afterAvailable, _ := afterAcc.GetAvailableAmount(beforeBalance.CurrencyCode)
			afterFrozen, _ := afterAcc.GetFrozenAmount(beforeBalance.CurrencyCode)
			suite.Require().True(beforeBalance.Available.Equal(afterAvailable))
			suite.Require().True(beforeBalance.Frozen.Equal(afterFrozen))
		}
	}
}

// insertMockChangeLog used to insert mock change logs for testing
func (suite *PGDaoSuite) insertMockChangeLog(writeBalanceAccounts map[int64]*model.WriteAccount) []*model.EventApplyResult {
	n := 0
	idKeys := []string{}
	changeIDs := []int64{}
	accountIDs := []int64{}
	shardIDs := []int16{}
	userIDs := []int64{}
	currencyCodes := []string{}
	currencySymbols := []string{}
	availableDeltas := []decimal.Decimal{}
	frozenDeltas := []decimal.Decimal{}
	changeLogs := []*model.EventApplyResult{}

	for _, wa := range writeBalanceAccounts {
		for _, change := range wa.BalanceChangesMap {
			n++
			idKeys = append(idKeys, uuid.New().String())
			changeIDs = append(changeIDs, int64(n))
			accountIDs = append(accountIDs, wa.AccountID)
			shardIDs = append(shardIDs, int16(wa.ShardID))
			userIDs = append(userIDs, wa.UserID)
			currencyCodes = append(currencyCodes, string(change.CurrencyCode))
			currencySymbols = append(currencySymbols, string(change.CurrencyCode)) // assuming symbol is same as code for mock
			availableDeltas = append(availableDeltas, change.AvailableDelta)
			frozenDeltas = append(frozenDeltas, change.FrozenDelta)
			changeLogs = append(changeLogs, &model.EventApplyResult{
				ChangeID:       int64(n),
				IdempotencyKey: idKeys[len(idKeys)-1],
				Status:         model.ChangeLogStatusApplied,
			})
		}
	}

	_, err := suite.PGConn.Exec(suite.TestInstance.Ctx, `SELECT
		rand_insert_balance_change_logs($1::BIGINT, $2::TEXT[], $3::BIGINT[], $4::BIGINT[], $5::SMALLINT[], $6::BIGINT[],
		                                $7::TEXT[], $8::TEXT[], $9::NUMERIC[], $10::NUMERIC[]);`,
		n,
		pglib.Array(idKeys),
		pglib.Array(changeIDs),
		pglib.Array(accountIDs),
		pglib.Array(shardIDs),
		pglib.Array(userIDs),
		pglib.Array(currencyCodes),
		pglib.Array(currencySymbols),
		pglib.Array(availableDeltas),
		pglib.Array(frozenDeltas),
	)
	suite.Require().NoError(err, "failed to insert mock change logs")

	for _, writeAcc := range writeBalanceAccounts {
		_, err := suite.PGConn.Exec(suite.TestInstance.Ctx, `INSERT INTO accounts
			(id, user_id, shard_id, created_msec)
			VALUES($1, $2, $3, $4)`, writeAcc.AccountID, writeAcc.UserID, writeAcc.ShardID, time.Now().UnixMilli())
		if pg.IsDuplicateKeyError(err) {
			continue
		}
		suite.Require().NoError(err, "failed to insert mock accounts")
	}

	return changeLogs
}
