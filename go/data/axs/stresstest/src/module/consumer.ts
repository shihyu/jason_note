import { bytesToUtf8, EnvConfig } from "../module/utils";

import { Trend, Counter } from 'k6/metrics';


import {
    Reader
} from "k6/x/kafka";


const balanceChangeTotalMessagesConsumedCounter = new Counter('axs_total_consumed_count');
const balanceChangeTotalThroughputTrend = new Trend('axs_e2e_throughput_msg_per_sec');
const totalDurationTrend = new Trend('axs_total_duration_sec');
const e2eLatencyTrend = new Trend('axs_e2e_latency_mill_sec');
const balanceChangeInQueueLatencyTrend = new Trend('axs_inqueue_latency_ms');
const balanceChangeMsgDelayCountTrend = new Trend('axs_message_delay_count');
const balanceChangeBatchMsgCountTrend = new Trend('axs_batch_message_count');
const balanceChangeProcessorThroughputTread = new Trend('axs_processor_throughput_msg_per_sec');
const balanceChangeTotalProcessTimeTrend = new Trend('axs_total_process_time_cost_ms');
const balanceChangeDecodeTimeTrend = new Trend('axs_decode_time_cost_micro_sec');
const balanceChangeApplyTimeTrend = new Trend('axs_apply_time_cost_micro_sec');
const balanceChangeAsyncTimeTrend = new Trend('axs_async_cost_micro_sec');


export function consumeBalanceChangeResults({ config }: { config: EnvConfig }) {
    const reader = new Reader({
        brokers: config.KAFKA_BROKERS.split(','),
        topic: config.KAFKA_TOPIC,
        offset: config.KAFKA_CONSUME_OFFSET,
    })

    let totalMsgConsumed = 0;
    let firstCreatedMsec = 0;
    let lastPublishedMsec = 0;
    let firstProcessorStartedMsec = 0;
    let lastOffset = -1;
    while (true) {
        const messages = reader.consume({ limit: 1, timeout: '5s' });
        if (messages && messages.length > 0) {
            const msg = messages[0];
            const receivedMsec = Date.now();
            const text = bytesToUtf8(msg.value);
            try {
                const messageValue = JSON.parse(text);
                const startMsec = messageValue.event_created_msec;
                const publishedMsec = messageValue.published_msec;
                if (firstCreatedMsec === 0 || parseInt(startMsec) < firstCreatedMsec) {
                    firstCreatedMsec = parseInt(startMsec);
                }
                if (firstProcessorStartedMsec === 0 || parseInt(messageValue.start_process_msec) < firstProcessorStartedMsec) {
                    firstProcessorStartedMsec = parseInt(messageValue.start_process_msec);
                }
                if (parseInt(publishedMsec) > lastPublishedMsec) {
                    lastPublishedMsec = parseInt(publishedMsec);
                }
                if (messageValue.delay_count) {
                    balanceChangeMsgDelayCountTrend.add(messageValue.delay_count);
                }
                const latency = parseInt(publishedMsec) - parseInt(startMsec);
                e2eLatencyTrend.add(latency);
                balanceChangeTotalProcessTimeTrend.add(parseInt(messageValue.process_cost));
                balanceChangeDecodeTimeTrend.add(parseInt(messageValue.decode_cost));
                balanceChangeApplyTimeTrend.add(parseInt(messageValue.apply_cost));
                balanceChangeAsyncTimeTrend.add(parseInt(messageValue.async_cost));

                balanceChangeInQueueLatencyTrend.add(parseInt(messageValue.start_process_msec) - parseInt(messageValue.event_created_msec));

                balanceChangeBatchMsgCountTrend.add(parseInt(messageValue.total_messages));
                totalMsgConsumed += parseInt(messageValue.total_messages);
                balanceChangeTotalMessagesConsumedCounter.add(parseInt(messageValue.total_messages));

                balanceChangeProcessorThroughputTread.add(
                    parseInt(messageValue.total_messages) /
                    (parseInt(messageValue.process_cost) / 1000000)
                );

                lastOffset = msg.offset;
                if (totalMsgConsumed >= config.TOTAL_MESSAGES) {
                    console.log(`[VU ${__VU}] Reached 100 messages, stopping consumption.`);
                    break;
                }
            } catch (e) {
                console.error(`[VU ${__VU}] Failed to parse message: ${e}`);
            }
        } else {
            console.log(`[VU ${__VU}] No message received.`);
            break;
        }
    }

    if (totalMsgConsumed > 0 && lastPublishedMsec > firstCreatedMsec) {
        const durationSec = (lastPublishedMsec - firstCreatedMsec) / 1000;
        const throughput = totalMsgConsumed / durationSec;
        totalDurationTrend.add(durationSec);
        balanceChangeTotalThroughputTrend.add(throughput);
        console.log(`[VU ${__VU}] Total Messages Consumed: ${totalMsgConsumed}, Throughput: ${throughput.toFixed(2)} msg/sec, Last Offset: ${lastOffset}`);
    }
}
