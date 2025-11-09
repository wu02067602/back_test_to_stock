# back_test_to_stock


# 資料庫說明

這是一個 sqlite 資料庫，包含股票資料。
這裡面的股票資料是分鐘 K 線的資料，並且包含上市上櫃與興櫃的台股資料。
這些資料中如果股票有交易就會有資料，但是該分鐘沒有交易的話，就沒有該分鐘的資料。
成交量不會是零
股價不會是負的
上市與上櫃股票每天會開盤 4.5 小時，並且在資料中是以當日的 01:00 開始到 05:30
興櫃股票每天開盤 6 小時，並且在資料中是以當日的 01:00 開始到 07:00
由於資料中無法分辨上市櫃與興櫃的差異，因此請當成相同的項目處理。

CREATE TABLE IF NOT EXISTS daily_kbars (
                ts TIMESTAMP NOT NULL,
                stock_code TEXT NOT NULL,
                Open REAL NOT NULL,
                High REAL NOT NULL,
                Low REAL NOT NULL,
                Close REAL NOT NULL,
                Volume INTEGER NOT NULL,
                PRIMARY KEY (ts, stock_code)
            )