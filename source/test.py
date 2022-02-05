from datetime import datetime


def test():
    with open("app.log", 'r') as file:
        lines = file.readlines()
        dates = list()
        times = list()
        types = list()
        messages = list()
        for line in lines:
            l = line.strip().split(" ")
            if len(l[0]) > 0:
                if l[0][0] == "2":
                    dates.append(l[0])
                    times.append(l[1])
                    types.append(l[2])
                    messages.append(" ".join(str(item) for item in l[7:]))
                else:
                    messages[-1] += " ".join(str(item) for item in l) + "\n"

        given_type = input("Enter type of log(default is None[ERROR]): ")
        start_date = input("Enter start date of log(default is the beginning date[2020-01-31]): ")
        start_date = datetime.strptime(start_date, "%Y-%m-%d") if start_date else ""
        end_date = input("Enter end date of log(default is the end date[2020-01-31]): ")
        end_date = datetime.strptime(end_date, "%Y-%m-%d") if end_date else ""
        start_time = input("Enter start time of log(default is the beginning time[12:00:00]): ")
        start_time = datetime.strptime(start_time, "%H:%M:%S") if start_time else ""
        end_time = input("Enter end time of log(default is the end time[12:00:00]): ")
        end_time = datetime.strptime(end_time, "%H:%M:%S") if end_time else ""
        message_phrase = ""
        for i in range(len(dates)):
            if types[i] == given_type or given_type == "":
                if start_date <= datetime.strptime(dates[i], "%Y-%m-%d") <= end_date:
                    if start_time <= datetime.strptime(times[i], "%H:%M:%S") <= end_time:
                        if message_phrase in messages[i] or message_phrase == "":
                            print(dates[i] + " " + times[i] + " " + types[i] + " " + messages[i])


if __name__ == "__main__":
    test()
