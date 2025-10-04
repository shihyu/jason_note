### 編碼
- json.NewEncoder(<Writer>).encode(v)
- json.Marshal(&v)
### 解碼
- json.NewDecoder(<Reader>).decode(&v)
- json.Unmarshal([]byte, &v)
