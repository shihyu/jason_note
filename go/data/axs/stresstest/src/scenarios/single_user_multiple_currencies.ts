import grpc from 'k6/net/grpc';
import { getEnvConfig, EnvConfig, getRandomFloat } from "../module/utils";
import { consumeBalanceChangeResults } from "../module/consumer";
import { Options } from 'k6/options';
import { newDepositBalanceChangeEvent, newRandomBalanceChange } from '../types/balance_change_event';

import { check } from 'k6';

import {
  Connection
} from "k6/x/kafka";


export const options: Options = {
  scenarios: {
    producer_scenario: {
      executor: 'constant-vus',
      exec: 'invokeSubmitBalanceChangeEvents',
      vus: 10,
      duration: '10s',
    },

    consumer_scenario: {
      executor: 'per-vu-iterations',
      exec: 'runConsumeBalanceChangeResults',
      vus: 1,
      iterations: 1,
    },
  },
};



const client = new grpc.Client()
client.load(['../../pb/apipb'], './api.proto');

export function setup() {
  const envCfg = getEnvConfig();
  console.log(`Using Kafka Brokers: ${envCfg.KAFKA_BROKERS}`);
  console.log(`Using gRPC Endpoint: ${envCfg.GRPC_ENDPOINT}`);
  console.log(`Using Kafka Topic: ${envCfg.KAFKA_TOPIC}`);
  console.log(`Using Kafka Consume Offset: ${envCfg.KAFKA_CONSUME_OFFSET}`);
  console.log(`Using Total Messages to Consume: ${envCfg.TOTAL_MESSAGES}`);

  const connection = new Connection({ address: envCfg.KAFKA_BROKERS });
  const topics = connection.listTopics();
  console.log(`Available topics: ${topics.join(", ")}`);
  return { config: envCfg };
}

export function invokeSubmitBalanceChangeEvents({ config }: { config: EnvConfig }) {
  client.connect(config.GRPC_ENDPOINT, {
    plaintext: true,
  });

  const change1 = newRandomBalanceChange(-10000, 10000);
  const change2 = newRandomBalanceChange(-10000, 10000);
  const change3 = newRandomBalanceChange(-10000, 10000);
  const balanceChangeReq = newDepositBalanceChangeEvent("1", '1', [change1, change2, change3]);
  let response = client.invoke('/apipb.AccountBalanceService/BatchSubmitBalanceChanges', {
    requests: [balanceChangeReq],
  });

  check(response, {
    'status is OK': (r) => r && r.status === grpc.StatusOK,
  });

  client.close();


}

export function runConsumeBalanceChangeResults({ config }: { config: EnvConfig }) {
  consumeBalanceChangeResults({ config });
}