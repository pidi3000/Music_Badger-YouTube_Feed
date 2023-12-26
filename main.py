APP_VERSION = "1.4.0"


def main():
    import music_feed

    app = music_feed.create_app()

    print(app.url_map)

    from pathlib import Path

    cert_path = Path(app.config["SSL_CERT_PATH"]).absolute()
    key_path = Path(app.config["SSL_KEY_PATH"]).absolute()

    def print_part(part, indent_level=1, indent=4):
        PRINT_TYPE = False

        max_len = 0
        for key in part:
            padding = " "*indent * indent_level
            data = part[key]

            type_str = '' + str(type(data))
            type_str = f"{type_str}{' ' * max(30 - len(type_str), 0)} - " if PRINT_TYPE else ''

            key_str = '' + str(key)
            key_str = f"{key_str}{' ' * max(30 - len(key_str), 0)} - "

            if isinstance(data, dict):
                print(f"{padding}{type_str}{key_str} ->")
                # print(f"{padding} {type(data)} - {key}: ")
                # print(padding, type(data), " - ", key, ": ")
                key_len = print_part(
                    part=data,
                    indent_level=indent_level+1,
                    indent=indent
                )

            else:
                print(f"{padding}{type_str}{key_str} -> {data}")
                key_len = len(key)
                # print(padding, type(data), " - ", key, ": ", data)

            max_len = key_len if key_len > max_len else max_len

        return max_len

    print("-"*100)
    print(".")
    print(".")
    print("Version: ", APP_VERSION)
    print("")
    print_part(app.config)
    # print("DB_path: ", app.config["SQLALCHEMY_DATABASE_URI"])
    # print("")
    # print("SSL_ENABLE: ", app.config["MUSIC_FEED"]["SSL_ENABLE"])
    # print("SSL_ENFORCE: ", app.config["MUSIC_FEED"]["SSL_ENFORCE"])
    # print("SSL_CERT_PATH: ",
    #       app.config["MUSIC_FEED"]["SSL_CERT_PATH"], cert_path.exists())
    # print("SSL_KEY_PATH: ", app.config["MUSIC_FEED"]
    #       ["SSL_KEY_PATH"], key_path.exists())
    print(".")
    print(".")
    print("-"*100)

    context = None
    if app.config["SSL_ENABLE"]:
        # check ssl key and cert file exist

        if cert_path.exists() and key_path.exists():
            context = (str(cert_path), str(key_path))
        else:
            print(
                f"ERROR: SSL files not found. Key: {key_path.exists()}, Cert: {cert_path.exists()}")
            if app.config["SSL_ENFORCE"]:
                raise FileNotFoundError(
                    f"SSL files not found. Key: {key_path.exists()}, Cert: {cert_path.exists()}")

    print(context)
    if context is None:
        print("WARNING: running without ssl enabled")

    # app.run(host="0.0.0.0", port=app.config["PORT"], ssl_context=context)
    app.run(host="0.0.0.0", port=5000, ssl_context=context)


if __name__ == '__main__':
    main()
