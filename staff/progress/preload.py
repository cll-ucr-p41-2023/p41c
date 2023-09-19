username = cs_form.get("student")
cs_long_name = cs_content_header = f"Progress {('for ' + username) if username else ''}"
cs_handler = "passthrough"