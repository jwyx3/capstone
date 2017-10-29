### dump mongodb data

```
mongoexport --db used_car_ --collection sfbay_redis --type=csv --fields post_id,title,price,body,images,thumbs,posted_at,updated_at,notice,title_text,attr_text,url,category,dealer,address,latitude,longitude --out ./raw/sfbay.csv
mongoexport --db used_car_ --collection sfbay_redis --type=json --out ./raw/sfbay.json
```