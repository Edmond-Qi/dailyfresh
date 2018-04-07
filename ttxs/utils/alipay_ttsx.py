from alipay import AliPay
from django.conf import settings

def create_alipay():
    alipay = AliPay(
        # 验签
        appid=settings.APP_ID,
        app_notify_url=None,  # 默认回调url
        app_private_key_path=settings.APP_PRIVATE_KEY,
        alipay_public_key_path=settings.ALIPAY_PUBLIC_KEY ,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        sign_type="RSA2",
        # 使用沙箱环境就设置为True
        debug = True
    )
    return alipay

def pay(order_id,total):
    alipay = create_alipay()

    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=order_id,
        total_amount=str(total),
        subject="天天生鲜，订单支付",
        return_url=None,
        notify_url=None # 可选, 不填则使用默认notify url
    )
    return settings.ALIPAY_GATEWAY + order_string

def query(order_id):
    alipay = create_alipay()
    result = alipay.api_alipay_trade_query(out_trade_no=order_id)
    if result.get('code') == '10000' and result.get('trade_status') == "TRADE_SUCCESS":
        return True
    else:
        return False