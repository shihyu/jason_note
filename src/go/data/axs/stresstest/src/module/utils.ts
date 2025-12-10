
export function bytesToUtf8(bytes: ArrayLike<number>): string {
    // 先把每個 byte 變成「二進位字串」
    let binary = "";
    for (let i = 0; i < bytes.length; i++) {
        binary += String.fromCharCode(bytes[i]);
    }

    // 再把「類 latin1 的字串」轉成真正的 UTF-8 字串
    // decodeURIComponent(escape(...)) 是常見的 JS 小技巧
    try {
        return decodeURIComponent(escape(binary));
    } catch (_) {
        // 如果不是合法 UTF-8，就直接回傳 binary 版
        return binary;
    }
}

export interface EnvConfig {
    KAFKA_BROKERS: string; // 逗號分隔的 broker 列表
    GRPC_ENDPOINT: string; // gRPC 服務端點
    KAFKA_TOPIC: string; // Kafka 主題名稱
    KAFKA_CONSUME_OFFSET: number; // Kafka 消費起始偏移量
    TOTAL_MESSAGES: number; // 可選的總訊息數量
}

export function getEnvConfig(): EnvConfig {
    return {
        KAFKA_BROKERS: __ENV.KAFKA_BROKERS || "localhost:9092",
        GRPC_ENDPOINT: __ENV.GRPC_ENDPOINT || "localhost:1234",
        KAFKA_TOPIC: __ENV.KAFKA_TOPIC || "balance_change_stress_test_stats",
        KAFKA_CONSUME_OFFSET: parseInt(__ENV.KAFKA_CONSUME_OFFSET || "0", 10),
        TOTAL_MESSAGES: parseInt(__ENV.TOTAL_MESSAGES || "8000", 10),
    };
}

export function getRandomInt(min: number, max: number): number {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min)) + min;
}

export function getRandomFloat(min: number, max: number, decimalPlaces: number): number {
    const factor = Math.pow(10, decimalPlaces);
    const randomValue = Math.random() * (max - min) + min;
    return Math.floor(randomValue * factor) / factor;
}