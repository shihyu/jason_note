編譯項目
```shell
# cargo build
# cargo build --release
```

當我們在發佈的時候，需要進行編譯優化。編譯優化的配置需要再cargo.toml中進行配置。

```toml
[profile.dev]
opt-level = 0

[profile.release]
opt-level = 3
```