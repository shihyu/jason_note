import { SharedArray } from 'k6/data';

// 使用 SharedArray 來高效地在 VUs 之間共享大數據集
const users = new SharedArray('user data', function () {
    // 注意：__ENV.PWD 或 '.' 表示專案根目錄
    const data = JSON.parse(open('../data/users.json'));
    return data;
});

// 為了方便使用，可以在這裡定義一個隨機選擇的輔助函式
export function getRandomUser(min: number, max: number) {
    // 隨機選擇一個索引
    const randomIndex = Math.floor(Math.random() * (max - min)) + min;
    return users[randomIndex];
}