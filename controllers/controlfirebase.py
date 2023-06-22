from pyfcm import FCMNotification


class AlgoritmaPembelianResApi(http.Controller):

    

    def send_push_notification(api_key, device_id, message_title, message_body):
        apiKey = "AAAAkNDkUMM:APA91bGCLuOYapyAdkdCp-kyjDH9vJxDNMPy376OPA0yZS6UN9Fqv2WhhQ0EZ6tYHz0Sx3FR72ABp8XgrxJ_Enr0rQQjkqKyo3MWlJcImVv9LuIcqjxwNpgqECXqXzmQJ3kwz5bTTa9f";
        deviceId = "c0H-p3v8Q72tzO5Ff47peC:APA91bEttBicjwR4h5plpHiIN7Hzvv7IScP2IhpvkHpClIMe4W6bypf1z8II8dPtPbClfbHjlC6jURw5T3mtWZnx03xJS1gY7z8VYKYk0SIdkmwXHFHeYJEgy4bZtvQ1Czgjzl1mPYdX";
    
        message_title = "Uber update"
        message_body = "Hi john, your customized news for today is ready"

        push_service = FCMNotification(api_key=api_key)
        registration_id = device_id
        result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)
        # Response output
        res = {'status': 200, 'message': 'success', 'result': result}
        return json.dumps(res)
    