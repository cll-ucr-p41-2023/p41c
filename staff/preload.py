cs_header = cs_header + " Staff"
cs_long_name = cs_content_header = "Staff Interface"
cs_title = cs_title + " Staff"

cs_base_color = "#545454"
cs_light_color = "#a8a8a8"

cs_handler = "passthrough"

def cs_post_load(context):
    if not is_user_authorized("grade") and context.get("cs_content", "") != "":
        context['cs_content'] = "staff.py: Post load permission catch. This should not get here"