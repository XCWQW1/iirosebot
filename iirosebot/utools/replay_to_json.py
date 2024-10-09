def replay_to_json(text):
    try:
        text = text.split(" (hr_) ")
        reply_list = []
        num = 0
        for i in text:
            data = i.split(" (_hr) ")

            if len(data) == 1:
                reply_list[len(reply_list) - 1]['reply'] = data[0]
                break

            user_data = data[1].split("_")
            if num == 0:
                reply_list.append({"message": data[0], "user_name": user_data[0], "timestamp": user_data[1]})
            else:
                reply_list[len(reply_list) - 1]['reply'] = data[0]
                reply_list.append({"message": data[0], "user_name": user_data[0], "timestamp": user_data[1]})
            num += 1
        return reply_list
    except:
        return []