


關於pin的總結
- 被固定後不能再移動的類型有一個標記 trait !Unpin。
- 固定保證了實現了 !Unpin trait 的對象不會被移動
- 獲取已經被固定的 T 類型示例的 &mut T需要 unsafe
- 固定 !Unpin 對象到棧上需要 unsafe
- 固定 !Unpin 對象到堆上不需要 unsafe。Box::pin可以快速完成這種固定