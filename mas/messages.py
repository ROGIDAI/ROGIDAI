REQUEST = "request"
PROPOSE = "propose"
INFORM = "inform"

PROTOCOL = "mas4flp-custom"


def create_message(performative, sender, receiver, conversation_id,
                   content=None, reply_with=None, in_reply_to=None):
    return {
        "performative": performative,
        "sender": sender,
        "receiver": receiver,
        "protocol": PROTOCOL,
        "conversation_id": conversation_id,
        "content": content,
        "reply_with": reply_with,
        "in_reply_to": in_reply_to,
    }