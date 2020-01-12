import os
import re
import io
import json
import argparse 
import datetime
import requests 

from PIL import Image
from tqdm import tqdm
from bs4 import BeautifulSoup

BASE_URL = "https://www.dogdrip.net"

def parse(url: str, start_index: int, end_index: int, download_path: str = "./downloads"):
    create_dir_if_not(download_path)
    mid_form_url = convert_url_into_mid_format(url)
    num_of_announcement = get_number_of_announcement(mid_form_url)
    index_lst = range(start_index, end_index + 1)

    for i in tqdm(index_lst):
        parser_page(mid_form_url + str(i), download_path, num_of_announcement)

def parser_page(url: str, download_path: str, num_announce: int = None):
    """ takes in url as parameter
    url should contain list of posts like following 
    https://www.dogdrip.net/index.php?mid=duck&page=1 
    """
    if num_announce is None:
        num_announce = get_number_of_announcement(url)
    
    bsobj = get_soup_from_url(url)
    lst_tr = find_tr(bsobj)

    for tr in lst_tr[num_announce + 1:]:
        tr_dict = convert_tr_to_dict(tr)

        dir_name = sanitize_path(tr_dict["title"])
        maybe_dir_path = os.path.join(download_path, dir_name)
        dir_path = get_next_avaliable_dir_path(maybe_dir_path)
        create_dir_if_not(dir_path)
        tr_url = tr_dict["url"]
        download_imgs_from_url(tr_url, dir_path)

        try:
            post_content, post_comment_lst = get_post_content_and_comments(tr_url)
            tr_dict["post_content"] = post_content
            tr_dict["post_comment_lst"] = post_comment_lst

            write_as_json(tr_dict, dir_path)
        except:
            error_message = f"[Write Json Error] Fail to write Json for {tr_url}"
            write_to_log(error_message)
    
def download_imgs_from_url(url: str, download_path: str = "./test_download"):
    
    post_soup = get_soup_from_url(url)
    document_srl = get_document_srl(url)
    document_srl_soup = post_soup.select(f".document_{document_srl}_0")

    imgs, *_ = [i.select("img") for i in document_srl_soup]
    img_count = 1
    
    for img in imgs:
        img_url = BASE_URL + img["src"]
        download_img(img_url, download_path, img_count)
        img_count += 1

def download_img(img_url, path, img_count):
    
    img_name = img_count

    for i in range(3):
        try:
            r = requests.get(img_url)
        except:
            error_message = f"[GET ERROR] fail to get {img_url}"
            write_to_log(error_message)
    try:
        if r.status_code == 200:
                img = Image.open(io.BytesIO(r.content)).convert("RGB")
                img_format = img.format if img.format is not None else "jpeg"
                img_path = os.path.join(path, f"{img_name}.{img_format}")
                img.save(img_path)
    except Exception as e:
        error_message = f"[Write ERROR] fail to write {img_url}"
        write_to_log(error_message)

# Functions for convert tr_obj -> dict 

def convert_tr_to_dict(tr_obj):
    """ It parses info about post at surface
        (at https://www.dogdrip.net/index.php?mid=duck&page=1 level instead of going one level deeper)
    Example :
      result_dict = 
        {
            "postnum": "해당 글 번호",
            "url": "해당 글 url",
            "title": "해당 글 제목",
            "poster": "글쓴이",
            "num_of_thumup": "추천 수",
            "date": "글 작성 시간",
            "views": "조회수",
            "num_comments": "댓글 수",
            "image": 이미지가 존제하면 "1", 없으면 "0",
            "post_content": [
                "글 내용"
            ],
            "post_comment_lst": [
                {
                    "commentor": "댓글 작성자 닉네임",
                    "date": "댓글 작성 시간",
                    "comment": "댓글 내용",
                    "dogdrip_con": "개드립콘 존재시 개드립콘 url",
                    "reply_to": "다른 이에게 다는 답글일시 그 대상의 닉네임을, 아니면 빈 문자열을"
                }
            ]
        }
    """
    result_dict = {}

    result_dict["postnum"] = get_postnum(tr_obj)
    result_dict["url"] = get_url(tr_obj)    
    result_dict["title"] = get_title(tr_obj)
    result_dict["poster"] = get_poster(tr_obj)
    result_dict["num_of_thumup"] = get_num_of_thumup(tr_obj)
    result_dict["date"] = get_date(tr_obj)
    result_dict["views"] = get_views(tr_obj)
    result_dict["num_comments"] = get_num_comments(tr_obj)
    result_dict["image"] = get_image_or_not(tr_obj)
    return result_dict

# Helper functions for tr_obj

def get_postnum(tr_obj) -> str:
    return tr_obj.select('.ed.no')[0].text.strip()

def get_title(tr_obj) -> str:
    return tr_obj.select('span.ed.title-link')[0].text.strip()

def get_poster(tr_obj) -> str:
    return tr_obj.select('.author')[0].text.strip()

def get_url(tr_obj) -> str:
    href = tr_obj.select("a")[0]["href"]
    srl = re.match(".*document_srl=(\d+)", href)
    if srl is not None:
        return f"{BASE_URL}/{srl.group(1)}"
    else:
        return href 
"/index.php?mid=duck&sort_index=popular&page=1&document_srl=236491770"
def get_num_of_thumup(tr_obj) -> str:
    try:
        return tr_obj.select('.ed.voteNum.text-primary')[0].text.strip()
    except:
        return "-1"

def get_date(tr_obj) -> str:
    # YYYY-MM-DD
    return tr_obj.select('.time')[0].text.strip()

def get_views(tr_obj) -> str:
    try:
        return tr_obj.select('.readNum')[0].text.strip()
    except:
        return "-1"

def get_num_comments(tr_obj) -> str:
    try:
        return tr_obj.select('.ed.text-primary')[0].text.strip()
    except:
        return "0"

def get_image_or_not(tr_obj) -> str:
    # "1" for true, "0" for false
    return str(len(tr_obj.select('.ed.print-icon.margin-left-xxsmall')))

# Helper function for parse content within post
def get_post_content_and_comments(url):
    soup = get_soup_from_url(url)
    content =  get_post_content(soup)
    comments = get_post_comments(soup)
    return content, comments

def get_post_comments(soup):
    """ Only parses latest comments
    This is really naive way of parse comments.
    Since I really do not need comments for now, I will leave it as it is.
    """
    comment_lst = []
    comments = soup.select(".comment-list > .comment-item")

    for c in comments:
        comment_dict = {}
        
        commentor = c.select("span > span")[0].text
        date = c.select(".text-xsmall")[0].text
        comment = c.select("div.ed.margin-bottom-xxsmall.margin-left-xsmall")[0].text.strip()
        dogdrip_con = ""
        if comment == "":
            comment = c.select("div > .xe_content > a")[0].attrs['title']
            dogdrip_con = c.select("div > .xe_content > a")[0].attrs['style']
        
        reply_to = check_comment_reply(comment) if check_comment_reply(comment) is not None else ""

        comment_dict["commentor"] = commentor
        comment_dict["date"] = date
        comment_dict["reply_to"] = reply_to.replace("@", "")
        comment_dict["comment"] = comment if reply_to == "" else comment.replace(reply_to, "")
        comment_dict["dogdrip_con"] = dogdrip_con

        comment_lst.append(comment_dict)

    return comment_lst

def get_post_content(soup):
    """ Parses un-normalized contentent
    Can be improved by cleaning up \n characters
    """
    return [ s.text.strip().replace(u'\xa0', u' ')  if s != '' else None for s in soup.select(".ed.clearfix.margin-vertical-large > .xe_content") ]

def get_document_srl(url: str) -> str: 
    return re.search("net\/(\d*)", url).group(1)

#  Helper functions
def convert_url_into_mid_format(url: str) -> str:
    regular_board_name = re.search("net\/(\w*)$", url)
    if regular_board_name is not None:
        return f"https://www.dogdrip.net/index.php?mid={regular_board_name.group(1)}&page="  
    else :
        popular_board_name = re.match(".*mid=\w+\&sort_index=popular", "https://www.dogdrip.net/index.php?mid=duck&sort_index=popular")
        if popular_board_name is not None:
            return url + "&page="
        else :
            raise ValueError("Given url cannot be parsed")

def get_soup_from_url(url: str) -> str:
    r = requests.get(url)
    return BeautifulSoup(r.text, "html.parser")

def find_tr(bsobj):
    return bsobj.find_all("tr")

def get_number_of_announcement(url: str) -> int:
    bsobj = get_soup_from_url(url)
    lst_tr = find_tr(bsobj)
    return sum([1 if "공지" in t.text else 0 for t in lst_tr])

def write_as_json(bsobj, path):
    json_path = os.path.join(path, "info.json")
    with open(json_path, 'w') as file:
        json.dump(bsobj, file)

def write_to_log(message):
        with open(f"./logs", 'a') as file:
            file.write(str(datetime.datetime.now()) + " " + message + '\n')

def create_dir_if_not(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def get_next_avaliable_dir_path(dir_path: str) -> str:
    if not os.path.exists(dir_path):
        return dir_path
    else:
        i = 1
        while os.path.exists(dir_path + str(i)):
            i += 1
        return dir_path + "-" + str(i)

def sanitize_path(path):
    return re.sub(r'\\|\:|\?|\*|\"|\<|\>|\||\/|\.',"" , path)

def check_comment_reply(comment):
    result = re.search("(\@........)", comment)
    try:
        maybe_result = result.group(1)
    except Exception:
        maybe_result = None
    return maybe_result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="개드립 parser")
    parser.add_argument("--download_path", metavar='d', default="./downloads", type=str, help="파일이 다운될 주소입니다.")
    parser.add_argument("--url", metavar='u', type=str, help="파싱할 게시판 주소입니다.")
    parser.add_argument("--start_index", metavar='s', default=1, type=int, help="파싱할 게시판의 시작 페이지 번호입니다.")
    parser.add_argument("--end_index", metavar='e', default=50, type=int, help="파싱할 게시판의 마지막 페이지 번호입니다.")
    
    args = parser.parse_args()
    parse(args.url, args.start_index, args.end_index, args.download_path)