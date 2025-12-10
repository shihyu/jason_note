declare module 'k6/x/kafka' {   
    export class Reader {
        constructor(config: any);
        consume(config: any): any;
        commit(messages: any[]): void;
        close(): void;
    }

    export class Writer {
        constructor(config: any);
        produce(config: any): void;
    }

    export class Connection {
        constructor(config: any);
        createTopic(config: any): void;
        listTopics(): string[];
    }
    
    export const SCHEMA_TYPE_JSON: number;
    export const Trend: any; 
}