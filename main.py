APP_VERSION = "1.0.7"

if __name__ == '__main__':

    import music_feed

    # app.secret_key = 'REPLACE ME - this value is here as a placeholder.'
    app = music_feed.create_app()

    print(app.url_map)

    from music_feed._data.config import db_path

    print("-"*100)
    print(".\n"*2)
    print("Version: ", APP_VERSION)
    print("")
    print("DB_path: ", db_path)
    print(".\n"*2)
    print("-"*100)

    context = ('ssl/cert.pem', 'ssl/key.pem')

    app.run(host="0.0.0.0", port=5000, debug=True, ssl_context=context)
