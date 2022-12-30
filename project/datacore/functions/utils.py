def strip_word(word):
    if word.startswith("-"):
        word = word[1:]
    if word.endswith("-"):
        word = word[:-1]
    return word


def prepare_pagination(query, page=1, items_per_page=20, request_parameters={}):
    from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

    parameters = ""
    for k, v in request_parameters.items():
        if v and k != "page":
            parameters = f"{parameters}&{k}={v}"
    paginator = Paginator(query, items_per_page)
    adjacent_pages = 5
    page = int(page)
    start_page = max(page - adjacent_pages, 1)
    if start_page <= 3:
        start_page = 1
    end_page = page + adjacent_pages + 1
    if end_page >= paginator.num_pages - 1:
        end_page = paginator.num_pages + 1
    try:
        query = paginator.page(page)
    except PageNotAnInteger:
        query = paginator.page(1)
    except EmptyPage:
        query = paginator.page(paginator.num_pages)
    paginator_range = range(start_page, end_page)
    if request_parameters:
        return query, paginator_range, parameters
    else:
        return query, paginator_range


def get_or_create_dir(path):
    from pathlib import Path

    Path(path).mkdir(parents=True, exist_ok=True)


def download(url, path):
    # Download with progressbar
    import math

    import requests
    from tqdm.auto import tqdm

    r = requests.get(url, stream=True, allow_redirects=True)
    total_size = int(r.headers.get("content-length", 0))
    block_size = 1024
    with open(path, "wb") as f:
        for data in tqdm(
            r.iter_content(block_size),
            total=math.ceil(total_size // block_size),
            unit="KB",
            unit_scale=True,
        ):
            f.write(data)


def download_clean(url, path):
    # Clean download
    import requests

    r = requests.get(url, allow_redirects=True)
    open(path, "wb").write(r.content)
