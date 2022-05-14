a = {
    "customerData": {
        "customerName": "string",
        "customerCity": "string",
        "customerCityId": "string",
        "customerState": "string",
        "customerStateId": "string",
        "CustomerAddress": "string"

    },
    "data": [
        {
            "stockName": "string",
            "stockId": "int",
            "stockCity": "string",
            "stockCityId": "string",
            "stockState": "string",
            "stockStateId": "string",
            "shippingMethods": [
                {
                    "customerDiscount": "int",
                    "customerPrice": "int",
                    "method": "mahex",
                    "shipmentPrice": "int",
                    "shippingLabel": "ماهکس",
                    "selected": false,
                    "description": "تحویل یک تا سه روز کاری",
                    "methodType": "int 1: insurance, 2: receiver, 3: all",
                    "receiverInfo": null,
                    "insurance": {
                        "caculateFormula": {
                            "insurancePrice": "int",
                            "units": "int"
                        },
                        "coverPrice": {
                            "fullCart": {
                                "label": "بیشترین ارزش بسته",
                                "method": "max",
                                "value": "int"
                            },
                            "minFullCart": {
                                "label": "کمترین ارزش بسته",
                                "method": "min",
                                "value": "int"
                            },
                            "customRange": {
                                "label": "ارزش انتخابی",
                                "method": "selecting",
                                "value": "int"
                            }
                        }
                    }
                },
                {
                    "customerDiscount": "int",
                    "customerPrice": "int",
                    "method": "storage",
                    "shipmentPrice": "int",
                    "shippingLabel": "تحویل درب انبار",
                    "selected": false,
                    "description": "نیاز به اعلام نام پیک",
                    "methodType": "int 1: insurance, 2: receiver, 3: all",
                    "receiverInfo": {
                        "receivers": [
                            {
                                "name": "صغری",
                                "nationalCode": "string",
                                "mobileNumber": "string"
                            },
                            {
                                "name": "کبری",
                                "nationalCode": "string",
                                "mobileNumber": "string"
                            }
                        ],
                        "receiverTypes": [
                            {
                                "label": "پیک شخصی",
                                "value": 1
                            },
                            {
                                "label": "پیک عمومی",
                                "value": 2
                            },
                            {
                                "label": "پیک های ثبت شده ی قبلی",
                                "value": 3
                            }
                        ]
                    },
                    "insurance": {
                        "caculateFormula": {
                            "insurancePrice": "int",
                            "units": "int"
                        },
                        "coverPrice": {
                            "fullCart": {
                                "label": "بیشترین ارزش بسته",
                                "method": "max",
                                "value": "int"
                            },
                            "minFullCart": {
                                "label": "کمترین ارزش بسته",
                                "method": "min",
                                "value": "int"
                            },
                            "customRange": {
                                "label": "ارزش انتخابی",
                                "method": "selecting",
                                "value": "int"
                            }
                        }
                    }
                }
            ],
            "products": [
                {
                    "status": "in_cart",
                    "count": 1,
                    "warehouse": {
                        "id": 0,
                        "label": ""
                    },
                    "price": 42000000,
                    "specialPrice": 42000000,
                    "totalPrice": 42000000,
                    "systemCode": "100101002001",
                    "visibleInSite": true,
                    "name": "samsung galaxy s9",
                    "minCount": 1,
                    "maxCount": 1,
                    "config": {
                        "color": {
                            "value": "black",
                            "attributeLabel": "رنگ",
                            "label": "سیاه"
                        },
                        "guarantee": {
                            "value": "awat",
                            "attributeLabel": "گارانتی",
                            "label": "آوات"
                        },
                        "storage": {
                            "value": "16 GB",
                            "attributeLabel": "حافظه داخلی",
                            "label": "۱۶ گیگابایت"
                        },
                        "seller": {
                            "value": "Awat",
                            "attributeLabel": "فروشنده",
                            "label": "آوات"
                        },
                        "image": {
                            "url": "https://cdn.shopify.com/s/files/1/0289/1534/products/samsung-galaxy-s9-black-front-angle-view-1_1024x1024.jpg?v=1533374902",
                            "attributeLabel": "تصویر",
                            "label": "تصویر"
                        }
                    }
                }
            ]
        }
    ]
}
