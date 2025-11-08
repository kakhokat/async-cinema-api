from http import HTTPStatus


def test_film_detail_ok(client):
    film_id = "b31592e5-673d-46dc-a561-9446438aea0f"
    resp = client.get(f"/api/v1/films/{film_id}")
    assert resp.status_code == HTTPStatus.OK
    body = resp.json()
    assert body["uuid"] == film_id
    assert body["title"] == "Lunar: The Silver Star"
    assert body["imdb_rating"] == 9.2


def test_film_detail_not_found(client):
    resp = client.get("/api/v1/films/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == HTTPStatus.NOT_FOUND
    assert resp.json()["detail"] == "film not found"


def test_films_list_default_sort(client):
    resp = client.get("/api/v1/films?page_size=3&page_number=1")
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    # сортировка по умолчанию: -imdb_rating
    titles = [x["title"] for x in data]
    assert titles[0] == "Lunar: The Silver Star"  # 9.2
    assert titles[1] == "Wishes on a Falling Star"  # 8.5
    assert titles[2] == "Silent Moon"  # 7.0


def test_films_list_genre_filter(client):
    genre = "6f822a92-7b51-4753-8d00-ecfedf98a937"
    resp = client.get(f"/api/v1/films/?genre={genre}&page_size=10&page_number=1")
    assert resp.status_code == HTTPStatus.OK
    titles = [x["title"] for x in resp.json()]
    assert titles == ["Lunar: The Silver Star", "Silent Moon"]


def test_films_pagination(client):
    # всего 5 фильмов; проверим, что пагинация корректна
    page1 = client.get("/api/v1/films?page_size=2&page_number=1").json()
    page2 = client.get("/api/v1/films?page_size=2&page_number=2").json()
    page3 = client.get("/api/v1/films?page_size=2&page_number=3").json()

    assert len(page1) == 2
    assert len(page2) == 2
    assert len(page3) == 1  # остался последний

    # убедимся в отсутствии дублей между страницами
    ids = [x["uuid"] for x in page1 + page2 + page3]
    assert len(ids) == len(set(ids))


def test_films_search(client):
    # найдём по слову "star" (есть в 3 фильмах)
    resp = client.get("/api/v1/films/search?query=star&page_size=10&page_number=1")
    assert resp.status_code == HTTPStatus.OK
    titles = [x["title"] for x in resp.json()]
    # ожидание: сначала Lunar (9.2), потом Wishes (8.5), потом Billion Star Hotel (6.1)
    assert titles[:3] == [
        "Lunar: The Silver Star",
        "Wishes on a Falling Star",
        "Billion Star Hotel",
    ]
