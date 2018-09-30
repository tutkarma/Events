import requests
import time
import json


def replace_id_movies(dict_showings, dict_movies):
    for rec in dict_showings["results"]:
        try:
            movie_title = dict_movies[rec["movie"]["id"]]
            rec["title"] = rec.pop("movie")
            rec["title"] = movie_title
        except Exception as ex:
            print("Не удалось поменять id на movie", ex)

def fix_dict_movies(new_movies, dict_movies):
    for rec in dict_movies['results']:
        new_movies[rec["id"]] = rec["title"]
    return new_movies


def replace_id_place(dict_events):
    for rec in dict_events['results']:
        try:
            id = rec['place']
            get_coords = requests.get("https://kudago.com/public-api/v1.4/places/{0}/?\\"
                                     "fields=coords".format(id), stream=True)
            if 'detail' in get_coords.json():
                rec['coords'] = {'lat': 0.0, 'lon': 0.0}
            else:
                rec['coords'] = get_coords.json()['coords']
        except Exception as ex:
            print("Не удалось добавить coords", ex)


def fix_place(dict_events):
    for rec in dict_events['results']:
        if rec['place'] is not None:
            rec['place'] = rec['place']['id']


if __name__ == "__main__":
    start = int(time.time()) - 1209600

    events = requests.get("https://kudago.com/public-api/v1.4/events/? \\"
                          "page=1&page_size=100&fields=id,dates,title,place,description,price \\"
                          "&location=msk", stream=True)

    data = {'events':{'results':[]},
            'places':{'results':[]},
            'showings':{}
            }

    try:
        events = requests.get("https://kudago.com/public-api/v1.4/events/? \\"
                          "page_size=100&fields=id,dates,title,place,description,price \\"
                          "&location=msk", stream=True)
        if events.status_code == 200:
            res = events.json()['results']
            # check doubles
            for j in res:
                if j not in data['events']['results']:
                    data['events']['results'].append(j)
        for i in range(1, 21):
            if events.json()["next"] is not None and events.json()["results"] is not None:
                events = requests.get(events.json()["next"], stream=True)
                if events.status_code == 200:
                    res = events.json()['results']
                    # check doubles
                    for j in res:
                        if j not in data['events']['results']:
                            data['events']['results'].append(j)
            else:
                break
    except Exception as ex:
        print("Не удалось получить ивенты", ex)

    fix_place(data['events'])
    replace_id_place(data['events'])
    print("Events done")

    try:
        places = requests.get("https://kudago.com/public-api/v1.4/places/? \\"
                                  "page_size=100&fields=id,title,address,timetable,phone,description,coords&location=msk", stream=True)
        if places.status_code == 200:
            res = places.json()['results']
            # check doubles
            for j in res:
                if j not in data['places']['results']:
                    data['places']['results'].append(j)
        #while True:
        for i in range(1, 6):
            if places.json()["next"] is not None and places.json()["results"] is not None:
                places = requests.get(places.json()["next"], stream=True)
                if places.status_code == 200:
                    res = places.json()['results']
                    # check doubles
                    for j in res:
                        if j not in data['places']['results']:
                            data['places']['results'].append(j)
            else:
                break
    except Exception as ex:
        print("Не удалось получить места", ex)
    print("Places done")

    dict_movies = {}
    try:
        for i in range(1, 41):
            movies = requests.get("https://kudago.com/public-api/v1.4/movies/?page={0}&page_size=100&fields=id,title".format(i), stream=True)

            if movies.status_code == 200:
                tmp_movies = movies.json()
                dict_movies = fix_dict_movies(dict_movies, tmp_movies)
    except Exception as ex:
        print("Не удалось получить фильмы", ex)
    print("Movies done")

    showings = requests.get("https://kudago.com/public-api/v1.4/movie-showings/? \\"
                            "page_size=100&fields=id,movie,place,datetime,price,&actual_since={0}&location=msk".format(start), stream=True)
    if showings.status_code == 200:
        dict_showings = showings.json()
        replace_id_movies(dict_showings, dict_movies)
        data['showings'] = dict_showings

    fix_place(data['showings'])
    print("Showings done")

    with open('data_maps.json', 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False)