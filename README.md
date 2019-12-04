# dogdrip-parser
python parser for dogdrip.net

# 개드립 파서 

[DogDrip.net](https://www.dogdrip.net/)에 있는 글들을 다운로드해주는 파서입니다.

## 파싱된 파일 예시

```bash
├── downloads
    ├── {글 제목1}
    │   ├── {글에 첨부된 이미지}
    │   └── info.json
    └── {글 제목2}
        └── info.json
```

### info.json 

```json
{
    "postnum": "해당 글 번호",
    "url": "해당 글 url",
    "title": "해당 글 제목",
    "poster": "글쓴이",
    "num_of_thumup": "추천 수",
    "date": "글 작성 시간",
    "views": "조회수",
    "num_comments": "댓글 수",
    "image": "이미지가 존재하면 1, 없으면 0",
    "post_content": [
        "글 내용"
    ],
    "post_comment_lst": [
        {
            "commentor": "댓글 작성자 닉네임",
            "date": "댓글 작성 시간",
            "comment": "댓글 내용",
            "dogdrip_con": "개드립콘 존재시 개드립콘 url"
        }
    ]
}
```


## 예시

`python3 parser.py --download_path ./downloads --url "https://www.dogdrip.net/duck" --start_index 1 --end_index 50`

`--url "https://www.dogdrip.net/duck"` : https://www.dogdrip.net/duck 에 있는 글들을 

`--start_index 1` : 1 페이지 부터 

`--end_index 50` : 50 페이지 까지

`--download_path ./downloads` : 현재 다이렉토리 안에 `downloads` 폴더에 저장합니다.

## 사용법

0. python3.6+ 사용을 권장합니다. CMD 또는 터미널에 

* `python --version`
* `python3 --version`

1. 깃 클론. 현재 보고 계신 리포를 원하시는 위치에 클론해 주세요 

* `git clone https://github.com/hyunR/dogdrip-parser`

2. 클론된 다이렉토리에 이동 후 `pip`를 이용해 필요한 라이브러리들을 설치해 주세요.

* `cd dogdrip-parser`
* `pip install -r requirements.txt`
* `pip3 install -r requirements.txt`

3. 파이썬을 이용해 `parser.py` 파일을 실행시켜 주세요.

* `python3 parser.py --download_path ./downloads --url https://www.dogdrip.net/duck --start_index 1 --end_index 50`

## 웹 파싱하실때 읽어주세요.

[다음 글을 읽어주세요](https://www.scrapehero.com/how-to-prevent-getting-blacklisted-while-scraping/)

1. `Robots.txt` 를 존중해주세요. 2019년 12월 03일 기준 개드립에는 `Robots.txt`가 존재하지 않지만, 후에 생겨난다면 존중해주세요.
2. 멀티 스레딩을 피해주세요. 현재 파서는 멀티 프로세싱을 사용하지 않아 속도가 느립니다. 하지만 개드립 서버에 주어지는 부하를 줄이기 위해 멀티 스레딩은 지양해주세요.
3. 2번과 같은 이유에서 개드립 피크타임(저녁때 부터 새벽까지)에는 파싱을 지양해주세요.
4. 과도한 파싱시 ip가 차단당할 수도 있습니다.