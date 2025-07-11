#!/usr/bin/env python3
"""
Script to analyze method signatures for APIs that failed due to parameter issues.
"""

import inspect
import sys

sys.path.insert(0, ".")

from follow_up_boss.client import FollowUpBossApiClient


def analyze_api_signatures():
    client = FollowUpBossApiClient()

    print("=== API Method Signatures Analysis ===\n")

    # Calls API
    try:
        from follow_up_boss.calls import Calls

        calls_api = Calls(client)
        sig = inspect.signature(calls_api.create_call)
        print(f"Calls.create_call: {sig}")
    except Exception as e:
        print(f"Calls API error: {e}")

    # Text Messages API
    try:
        from follow_up_boss.text_messages import TextMessages

        text_api = TextMessages(client)
        sig = inspect.signature(text_api.create_text_message)
        print(f"TextMessages.create_text_message: {sig}")
    except Exception as e:
        print(f"TextMessages API error: {e}")

    # Webhooks API
    try:
        from follow_up_boss.webhooks import Webhooks

        webhooks_api = Webhooks(client)
        sig = inspect.signature(webhooks_api.create_webhook)
        print(f"Webhooks.create_webhook: {sig}")
    except Exception as e:
        print(f"Webhooks API error: {e}")

    # Deals API
    try:
        from follow_up_boss.deals import Deals

        deals_api = Deals(client)
        sig = inspect.signature(deals_api.create_deal)
        print(f"Deals.create_deal: {sig}")
    except Exception as e:
        print(f"Deals API error: {e}")

    # Email Marketing API
    try:
        from follow_up_boss.email_marketing import EmailMarketing

        em_api = EmailMarketing(client)
        methods = [m for m in dir(em_api) if not m.startswith("_")]
        print(f"EmailMarketing available methods: {methods}")
    except Exception as e:
        print(f"EmailMarketing API error: {e}")

    # Action Plans API
    try:
        from follow_up_boss.action_plans import ActionPlans

        ap_api = ActionPlans(client)
        methods = [m for m in dir(ap_api) if not m.startswith("_")]
        print(f"ActionPlans available methods: {methods}")
    except Exception as e:
        print(f"ActionPlans API error: {e}")

    # Groups API (to understand the user requirement issue)
    try:
        from follow_up_boss.groups import Groups

        groups_api = Groups(client)
        sig = inspect.signature(groups_api.create_group)
        print(f"Groups.create_group: {sig}")
    except Exception as e:
        print(f"Groups API error: {e}")


if __name__ == "__main__":
    analyze_api_signatures()
