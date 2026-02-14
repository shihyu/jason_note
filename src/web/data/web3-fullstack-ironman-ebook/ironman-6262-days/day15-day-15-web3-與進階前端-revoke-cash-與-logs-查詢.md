# DAY 15｜Day 15 - Web3 與進階前端：Revoke Cash 與 Logs 查詢

- 原文：https://ithelp.ithome.com.tw/articles/10326582
- 發佈時間：2023-09-24 14:40:29

## 章節內容

### 1. 未分章內容

我們又回到了 Web3 與前端的主題，今天會介紹一個實用的查看地址所有 Token Approval、方便撤銷授權的網站 revoke.cash，以及它背後的實作原理，也就是 Event Log 的查詢方式，可以讓我們對區塊鏈上的資料有更深入的了解。

### 2. Token Approval 的危險

若是使用 EVM 鏈一段時間後的使用者，可能會授權過許多 DApp 使用自己的 Token，例如要做 Token 交易時需要授權 Uniswap, 1inch 等 DEX 智能合約使用自己的 ERC-20 Token，或是如果要掛賣 NFT 就要授權 Opensea, blur 等合約使用自己的 ERC-721, ERC-1155 Token，累積久了之後可能就不記得自己曾經 Approve 過什麼合約了。

但這就會有個風險：萬一某個合約被駭客發現漏洞，那駭客可能可以用這個合約的身份，轉走所有 Approve 過這個合約的地址的 Token。因為只要駭客能發送惡意交易讓合約內的程式碼執行到去轉移 ERC-20 Token 的那行邏輯（例如 `token.transferFrom(user, to, amount)` ），並且控制 to address 為自己的地址，那就能把那些地址的 token 轉走。

一般智能合約當然會在這個邏輯附近做嚴格的檢查，但有時還是會有意想不到的漏洞產生。例如[這裡](https://revoke.cash/exploits)列出了許多因為合約被駭加上 Token Approval 導致使用者的錢被轉走的事件，甚至連知名的 Sushiswap 也有[被駭過](https://rekt.news/sushi-yoink-rekt/)。

因此如果是常使用的地址，一個好的習慣是常去確認自己的地址有沒有 Approve 過一些目前已經根本用不到的合約，趁 gas fee 低的時候把授權 Revoke 掉，就可以降低被駭客事件影響到的機率。有幾個服務都有提供授權查詢的工具，包含：

* [Revoke.cash](https://revoke.cash/)
  * [Etherscan Token Approval Checker](https://etherscan.io/tokenapprovalchecker)

### 3. Revoke Cash

進到 [Revoke.cash](https://revoke.cash/) 網站後可以隨便搜尋一個地址或域名（或是連接自己的錢包也可以），例如 `doge.eth` 這個 ENS domain，可以看到像這樣的畫面：

![https://ithelp.ithome.com.tw/upload/images/20230924/20162294TpgZFjN7Fd.png](../ironman-6262-assets/images/day15-img001-a5a8f73db8.png)

他會把所有這個地址曾經持有過的 Token，以及使用者是否有 Approve 過這些 Token、Approve 給哪個合約、上次操作日期等等資訊全部展示出來，也在最後有個 Revoke 的按鈕可以方便取消授權。所以像圖中有些舊的合約（Blur old, Opensea old）如果用不到了就可以撤銷掉。另外他也支援切換不同的 EVM 鏈查看授權，只要按右邊的鏈的 icon 就可以選擇。

![https://ithelp.ithome.com.tw/upload/images/20230924/20162294O58OSnV8QY.png](../ironman-6262-assets/images/day15-img002-9badf3d330.png)

至於他是怎麼知道一個地址過去所有 Approve 過的紀錄？這就要到鏈上拿 Event Logs 的資料了。

### 4. Event Logs

回顧 Day 8 中其實已經有講到 Event 的概念，也就是在智能合約中可以定義一些關鍵狀態改變的 Event，並在對應的時機發出，那天提到 ERC-20 標準中定義了以下格式的 Event：

[code]
    event Transfer(address indexed from, address indexed to, uint value);

[/code]

以及[這筆交易](https://sepolia.etherscan.io/tx/0x8778dfe09585097badb32951bc34a1cb41c166045bd37f6b92885b40f5c26bfc#eventlog)裡有個 ERC-20 Transfer Event 的範例，這是我轉移 UNI Token 的交易。而每個交易的 Logs tab 都可以看到這筆交易觸發了哪些 Event（一筆交易可以有非常多 Event）。

![https://ithelp.ithome.com.tw/upload/images/20230924/20162294iPw8v88TXa.png](../ironman-6262-assets/images/day15-img003-9cdf761a69.png)

從這張圖由上而下來介紹每個欄位的意義。首先 Address 代表是發出這個 Event 的智能合約地址，可以看到跟 UNI Token Contract Address 是一致的。再來是 Event Name，欄位的型別跟名稱都算好理解，但裡面的 `index` 還沒有介紹過。 `index_topic_1` 跟 `index_topic_2` 就對應到 Event 定義中的 `indexed` 標記，代表區塊鏈是否應該要對這個欄位做 indexing。實際的效益就是大家可以方便用有被 index 的欄位去 Filter 出 Logs，例如當我想找出我的地址所有轉出的 Transfer Event，那我只要 Filter 出 from 欄位是我的地址的所有 Event Logs 就可以了（後面會提到實際做法）。

而 amount 這個欄位在定義中沒有 `indexed` 代表不會被 index，也就是無法有效率地找到所有 Transfer amount 等於特定值的 Logs，這也是合理的因為這種使用場景很少，而且要使用 indexed 欄位所需要的 gas fee 也比較高。

接下來是 Topics，Topics 指的是一個 Log 中有被 index 的欄位們，而 Topic 0 會是從 Event 的定義計算 keccak256 hash 算出的值，可以用來辨識不同的 Event，計算方法如下：（圖片參考[網址](https://medium.com/mycrypto/understanding-event-logs-on-the-ethereum-blockchain-f4ae7ba50378)）

![https://ithelp.ithome.com.tw/upload/images/20230924/20162294zj959dSD5f.png](../ironman-6262-assets/images/day15-img004-e55b90112c.png)

所以其實要找出所有我的地址的轉出 Event，需要下的 Filter 會是 topic 0 = `0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef` 且 topic 1 = `0x00000000000000000000000032e0556aec41a34c3002a264f4694193ebcf44f7` 才能精準拿到對的 Logs 資料。注意到因為每個 topic 都固定是 32 bytes 的，所以如果是地址的話前面要 pad 一些 0。

最後是 Data 欄位，這裡就會依序放入沒有被 index 的欄位的值，因為 Transfer Event 只有 amount 欄位沒有被 index，所以 Data 裡的值就只有他。有了以上知識後，就可以試著使用 Alchemy 的 [eth_getLogs](https://docs.alchemy.com/reference/eth-getlogs) API 來查詢我的地址發出過的 UNI Token Transfer Event 有哪些：

[code]
    curl --request POST \
         --url https://eth-sepolia.g.alchemy.com/v2/YOUR_API_KEY \
         --header 'accept: application/json' \
         --header 'content-type: application/json' \
         --data '
    {
      "id": 1,
      "jsonrpc": "2.0",
      "method": "eth_getLogs",
      "params": [
        {
          "address": [
            "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984"
          ],
          "fromBlock": "0x0",
          "toBlock": "latest",
          "topics": [
            "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
            "0x00000000000000000000000032e0556aec41a34c3002a264f4694193ebcf44f7"
          ]
        }
      ]
    }' | jq

[/code]

把 `YOUR_API_KEY` 代換成讀者的 API Key 即可。topics 欄位代表 log topics 的值依序要等於什麼，以及會多指定 fromBlock 跟 toBlock 代表要查詢的區塊範圍，因為有時 Logs 的數量非常多會需要分頁查詢。查詢結果如下：

![https://ithelp.ithome.com.tw/upload/images/20230924/20162294MNvpllSqwq.png](../ironman-6262-assets/images/day15-img005-97fb06d340.png)

可以看到他會回傳所有符合的 Logs 的 Topics, Data, Transaction Hash, Block number 等等，而從 Topics 與 Data 就可以解析出這筆 Transfer Event Log 中的 from, to, amount 資料了。

### 5. Revoke Cash 程式碼

理解以上 Event Logs 的概念後，就可以來看 Revoke Cash 的程式碼，以下會簡單帶讀者看一下裡面核心邏輯的部分，不會解釋到每個細節。程式碼在[這裡](https://github.com/RevokeCash/revoke.cash)。

首先他需要拿到一個地址所有跟 Approve 有關的 Logs，相關的邏輯在 [useEvents.ts](https://github.com/RevokeCash/revoke.cash/blob/master/lib/hooks/ethereum/events/useEvents.tsx) 裡，傳入的參數有當下正在查詢的錢包地址以及 Chain ID：

[code]
    export const useEvents = (address: Address, chainId: number) => {
      // ...

    	const getErc721EventSelector = (eventName: 'Transfer' | 'Approval' | 'ApprovalForAll') => {
    	  return getEventSelector(getAbiItem({ abi: ERC721_ABI, name: eventName }));
    	};

    	const addressTopic = address ? addressToTopic(address) : undefined;
    	const transferToTopics = addressTopic && [getErc721EventSelector('Transfer'), null, addressTopic];
    	const transferFromTopics = addressTopic && [getErc721EventSelector('Transfer'), addressTopic];
    	const approvalTopics = addressTopic && [getErc721EventSelector('Approval'), addressTopic];
    	const approvalForAllTopics = addressTopic && [getErc721EventSelector('ApprovalForAll'), addressTopic];

    	const baseFilter = { fromBlock: 0, toBlock: blockNumber };

    	const {
    	  data: transferTo,
    	  isLoading: isTransferToLoading,
    	  error: transferToError,
    	} = useLogs('Transfer (to)', chainId, { ...baseFilter, topics: transferToTopics });

    	const {
    	  data: transferFrom,
    	  isLoading: isTransferFromLoading,
    	  error: transferFromError,
    	} = useLogs('Transfer (from)', chainId, { ...baseFilter, topics: transferFromTopics });

    	const {
    	  data: approval,
    	  isLoading: isApprovalLoading,
    	  error: approvalError,
    	} = useLogs('Approval', chainId, { ...baseFilter, topics: approvalTopics });

    	const {
    	  data: approvalForAllUnpatched,
    	  isLoading: isApprovalForAllLoading,
    	  error: approvalForAllError,
    	} = useLogs('ApprovalForAll', chainId, { ...baseFilter, topics: approvalForAllTopics });

    // ...
    }

[/code]

裡面使用 ERC-721 的 Event Selector 原因是 ERC-721 的 Transfer, Approval Event 的 Selector 都跟 ERC-20 是一樣的（像前者都等於 `keccak256('Transfer(address,address,uint256)')` ），因此可以重複使用。以及使用 `useLogs` 去查詢鏈上符合這些 topics 的 Logs，他基本上就是用 React Query 把查詢鏈上資料的 API Call 包起來的 Hook。

除了 Approval 相關的 Logs 以外他也拿了 Transfer From 跟 Transfer To 的資料，也就是從這個地址轉出/轉入特定 Token 的紀錄，就能用來計算當下這個地址擁有該 Token 的數量。

有了這些 Events 之後就可以用它來計算所有的 Token Approval 資料，由於 ERC-20、ERC-721、ERC-1155 的處理都不太一樣，我們先只專注看 ERC-20。相關的邏輯是在 [allowances.ts](https://github.com/RevokeCash/revoke.cash/blob/master/lib/utils/allowances.ts) 中，前面先對所有 Events 按照 Token Contract 做 Grouping，再按照 Contract Address 一個一個處理，而關於 ERC-20 的處理最關鍵是在這兩個 function：

[code]
    export const getErc20AllowancesFromApprovals = async (
      contract: Erc20TokenContract,
      owner: Address,
      approvals: Log[],
    ) => {
      const sortedApprovals = sortLogsChronologically(approvals).reverse();
      const deduplicatedApprovals = deduplicateLogsByTopics(sortedApprovals);

      const allowances = await Promise.all(
        deduplicatedApprovals.map((approval) => getErc20AllowanceFromApproval(contract, owner, approval)),
      );

      return allowances;
    };

    const getErc20AllowanceFromApproval = async (
      contract: Erc20TokenContract,
      owner: Address,
      approval: Log,
    ): Promise<BaseAllowanceData> => {
      const spender = topicToAddress(approval.topics[2]);
      const lastApprovedAmount = fromHex(approval.data, 'bigint');

      // If the most recent approval event was for 0, then we know for sure that the allowance is 0
      // If not, we need to check the current allowance because we cannot determine the allowance from the event
      // since it may have been partially used (through transferFrom)
      if (lastApprovedAmount === 0n) {
        return { spender, amount: 0n, lastUpdated: 0, transactionHash: approval.transactionHash };
      }

      const [amount, lastUpdated, transactionHash] = await Promise.all([
        contract.publicClient.readContract({
          ...contract,
          functionName: 'allowance',
          args: [owner, spender],
        }),
        approval.timestamp ?? blocksDB.getBlockTimestamp(contract.publicClient, approval.blockNumber),
        approval.transactionHash,
      ]);

      return { spender, amount, lastUpdated, transactionHash };
    };

[/code]

計算方式主要就是按照時間由新到舊排序 Logs 後，按照 topics 去做 deduplication，因為 Approval 的 event 長得像這樣： `Approval(address indexed owner, address indexed spender, uint value)` ，如果 topics 不同代表 `spender` 不同，因此需要分開處理。

針對同一個 owner 跟 spender 的組合，如果最新的一筆 Approval Log 的 Approval amount 是 0，那就代表這個地址已經撤銷授權了，可以直接 return 0。但如果不是的話，有可能這個地址在 Approve `spender` 後被 `spender` 使用過 `transferFrom` 把部分 Approve 的金額扣除（可以參考 ERC-20 transferFrom 的實作），因此才需要再去鏈上查詢一次 `allowance()` 知道最新的值。這樣就能拿到最精準的 Approval amount 了。

### 6. 小結

今天我們介紹了 Token Approval 背後的 Event Logs 原理，以及像 Revoke Cash 這種服務如何找出一個地址所有曾經 Approve 過的資料。可以看到這種查詢跟資料處理的邏輯其實非常複雜，因為要從鏈上最原始的 Logs 資料處理起去做好 aggregation，不過有了 Event Logs 的相關知識後就能一步一步把需要的資料組合出來了。明天會來介紹像 Metamask 這種錢包的 Browser Extension 背後是怎麼跟 DApp 互動的。
