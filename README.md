# mh_summary

## テスト


```bash
poetry run python src/main.py --help
poetry run python src/main.py test_data/0101.txt
poetry run python src/main.py test_data/0102.txt
poetry run python src/main.py test_data/0201.txt
poetry run python src/main.py --logseq test_data/0301_logseq.txt
```

## Config.tag_config

### identifier_dict

ticket_id

・3番め;の[<prefix>]から取得
```plaintext
'^[^;]+;[^;]+;\\[(チケット[^\\]]+)\\]'
```

・3番め;の[]から取得
```plaintext
'^[^;]+;[^;]+;\\[([^\\]]+)\\]'
```

・;[]から取得
```plaintext
';\\[(チケット.*?)\\]'
```
