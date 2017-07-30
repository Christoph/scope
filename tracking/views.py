from django.shortcuts import render
from pytracking import Configuration
from pytracking.django import OpenTrackingView, ClickTrackingView
from tracking.tasks import process_click_event, process_open_event


class MyOpenTrackingView(OpenTrackingView):

    def notify_tracking_event(self, tracking_result):
        # Override this method to do something with the tracking result.
        # tracking_result.request_data["user_agent"] and
        # tracking_result.request_data["user_ip"] contains the user agent
        # and ip of the client.
        process_open_event.delay(tracking_result)


class MyClickTrackingView(ClickTrackingView):

    def notify_tracking_event(self, tracking_result):
        # Override this method to do something with the tracking result.
        # tracking_result.request_data["user_agent"] and
        # tracking_result.request_data["user_ip"] contains the user agent
        # and ip of the client.
        process_click_event.delay(tracking_result)

