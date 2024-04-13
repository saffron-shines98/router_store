from locust import HttpUser, task, between


class MyUser(HttpUser):
    host = "https://noderetail-app-uat.plotch.ai"
    wait_time = between(1, 3)

    @task
    def update_status(self):
        headers = {
            "auth_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJjaGFsbGVuZ2Vfc3RyaW5nIjoiYTBhNTUyOWY5ZmE4Y2I4YmQ5MGM4M2VhY2ZlZGI3MTkuMjcyODgzIiwiaWF0IjoxNjk5NjI1NjI5fQ.p73OPbw1seApNxgAWS_SkeLKKNsL0oD3MMFB568Qucq0SVY52AueeXzfy5ZHmGwq6H3sVWCiDTMBaz0kNQSauQVJV2v-QiIFoADyazarrxCgTNvcJGa3VBjvw96gJA4H7QqWdVzNCyqXCu9VRnpxvUDAETQBBhmO7qf8KbW-fsxH2VFmygiOpGSGYYDG00ZMlzdyUqul56vwqX2kcZkEjL0zad7x7FrJY6ge5aeCrhIbUFctBQjyrvIjffwnaGpVvk_TpezIyFX5inIatrN8mJGstInMbIOvw99i26H1bijA_KbqNAjFvpKudwUBDHntCm8R75MenhAmHWOLqr17CGeco_IeghgcFR_FxpbuTfqKF7V5qNtR_Lhb4AMc8XzrNfPc2LhhT95nrjLy7-iFQa47SwT0pMeRM2rm4aNzUjSR3LDFpTTje8APM0p5FKER2umPnLnQiFGh1DSbSPJ-ypIjMWkuDrTKIV4idpzGCA3BEvfzU5zD3BHCLUx6XLgib0h_aPIOIwppRkvBEoIEVge7cvfNsYgScm0Q_s_bDwDbr0o4Ris0dHE4r4EP4pn5LforXSvFEzpajeTjM_P6PtTEVoD8r01EAbGr3nVj3bjOpG-IQq2jHQuGt_AkA1Q0YSNULndUyN7yLWaCw2av5XgwGBsmtqC_KfHvi4IoK8E",
            "nodesso_id": "272884"
        }

        payload = {"order_id": "58172787191", "order_status": "processing", "fulfilment_status": "shipped",
             "refund_status": 1, "status_created_time": "17:01:2024 17:14:37", "remark": "454",
             "noderetail_storefront_id": "12345"}
        self.client.post("/order/status/update", headers=headers, json=payload)