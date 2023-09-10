APP_VERSION = "1.1.0"


def main():
    import music_feed
    from data.config import Config
    config = Config()

    # app.secret_key = 'REPLACE ME - this value is here as a placeholder.'
    app = music_feed.create_app(config=config)

    print(app.url_map)

    print("-"*100)
    print(".")
    print(".")
    print("Version: ", APP_VERSION)
    print("")
    print("DB_path: ", app.config["SQLALCHEMY_DATABASE_URI"])
    print("")
    print("SSL_ENABLE: ", app.config["MUSIC_FEED"]["SSL_ENABLE"])
    print("SSL_CERT_PATH: ", app.config["MUSIC_FEED"]["SSL_CERT_PATH"])
    print("SSL_KEY_PATH: ", app.config["MUSIC_FEED"]["SSL_KEY_PATH"])
    print(".")
    print(".")
    print("-"*100)

    context = None
    if app.config["MUSIC_FEED"]["SSL_ENABLE"]:
        # check ssl key and cert file exist
        from pathlib import Path

        cert_path = Path(app.config["MUSIC_FEED"]["SSL_CERT_PATH"]).absolute()
        key_path = Path(app.config["MUSIC_FEED"]["SSL_KEY_PATH"]).absolute()

        print(cert_path.exists())
        print(key_path.exists())

        if cert_path.exists() and key_path.exists():
            context = (str(cert_path), str(key_path))
        else:
            print(
                f"ERROR: SSL files not found. Key: {key_path.exists()}, Cert: {cert_path.exists()}")
            if app.config["MUSIC_FEED"]["SSL_ENFORCE"]:
                return

    print(context)
    if context is None:
        print("WARNING: running without ssl enabled")

    app.run(host="0.0.0.0", port=5000, debug=True, ssl_context=context)


if __name__ == '__main__':
    main()
