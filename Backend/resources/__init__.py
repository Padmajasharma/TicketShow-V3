# backend/resources/__init__.py
from flask_restful import Api

from .auth import SignupResource, LoginResource
from .theatre import TheaterResource, TheaterUpdateResource
from .show import ShowResource, UpdateShowResource, ShowBookedSeatsResource, ShowByTMDBResource
from .files import UploadFileResource, UploadedFileResource
from .tickets import UserTicketsResource, TicketDetailResource, TicketDownloadResource, TicketCancelResource
from .booking import BookShowsResource
from .search import SearchTheatresResource, SearchShowsResource
from .user import UserProfileResource, RateShowResource
from .export import ExportTheatreResource
from .theatre_seats import TheatreSeatResource, TheatreSeatsResource
from .seat_holds import SeatHoldResource, SeatHoldReleaseResource
from .admin import (
    AdminShowsResource,
    AdminShowDetailResource,
    AdminTheatresResource,
    AdminTheatreDetailResource,
    AdminStatsResource,
    RecommendationsResource,
)
from .recommendations import ShowRecommendationsResource
from .seat_suggestion import SeatSuggestionResource
from .chatbot import ChatbotResource
from .otp import SendOtpResource, VerifyOtpResource
from .offers import OffersResource, OfferDetailResource, PricingResource
from .analytics import AnalyticsSalesResource
from .admin import (
    AdminStatsTimeseriesResource,
    AdminSeatImportResource,
    AdminSeatExportResource,
    AdminBulkShowsImportResource,
)


def register_resources(api: Api, app=None):
    """Register API resources. If `app` is provided, use `app.config['FEATURE_FLAGS']`
    to conditionally enable feature endpoints.
    """
    feature_flags = {}
    if app is not None:
        feature_flags = app.config.get('FEATURE_FLAGS', {}) or {}
    api.add_resource(SignupResource, "/signup", methods=["POST"])
    api.add_resource(LoginResource, "/login", methods=["POST"])
    api.add_resource(TheaterResource, "/theatres", methods=["POST", "GET"])
    api.add_resource(
        TheaterUpdateResource,
        "/theatres/<int:theatre_id>",
        methods=["GET", "PUT", "DELETE"],
    )
    api.add_resource(ShowResource, "/shows", methods=["POST", "GET"])
    api.add_resource(
        UpdateShowResource,
        "/shows/<int:show_id>",
        methods=["GET", "PUT", "DELETE"],
    )
    api.add_resource(ShowBookedSeatsResource, "/shows/<int:show_id>/booked-seats", methods=["GET"])
    api.add_resource(ShowByTMDBResource, "/shows/tmdb/<int:tmdb_id>", methods=["GET"])
    # Seat hold endpoints (place temporary holds on specific seat ids)
    api.add_resource(SeatHoldResource, "/shows/<int:show_id>/hold", methods=["POST"])
    api.add_resource(SeatHoldReleaseResource, "/shows/<int:show_id>/hold/<int:reservation_id>", methods=["DELETE"])
    api.add_resource(UploadFileResource, "/uploads", methods=["POST"])
    api.add_resource(UploadedFileResource, "/uploads/<filename>", methods=["GET"])
    api.add_resource(BookShowsResource, "/bookshows/<int:show_id>/book")
    # Tickets: user ticket listing, detail, download and cancel
    api.add_resource(UserTicketsResource, "/tickets", methods=["GET"])
    api.add_resource(TicketDetailResource, "/tickets/<int:ticket_id>", methods=["GET"])
    api.add_resource(TicketDownloadResource, "/tickets/<int:ticket_id>/download", methods=["GET"])
    api.add_resource(TicketCancelResource, "/tickets/<int:ticket_id>/cancel", methods=["POST"])
    api.add_resource(SearchTheatresResource, "/search/theatres", methods=["GET"])
    api.add_resource(SearchShowsResource, "/search/shows", methods=["GET"])
    api.add_resource(UserProfileResource, "/userprofile")
    api.add_resource(RateShowResource, "/rate/<int:show_id>", methods=["POST"])
    api.add_resource(ExportTheatreResource, "/export_theatre/<int:theatre_id>")
    api.add_resource(TheatreSeatResource, "/theatre_seats", methods=["POST", "DELETE"])
    api.add_resource(TheatreSeatsResource, "/theatres/<int:theatre_id>/seats", methods=["GET", "POST"])

    # Admin routes
    api.add_resource(AdminShowsResource, "/admin/shows")
    api.add_resource(AdminShowDetailResource, "/admin/shows/<int:show_id>")
    api.add_resource(AdminTheatresResource, "/admin/theatres")
    api.add_resource(AdminTheatreDetailResource, "/admin/theatres/<int:theatre_id>")
    api.add_resource(AdminStatsResource, "/admin/stats")
    # Recommendations is a feature-flagged endpoint
    if feature_flags.get('recommendations', True):
        api.add_resource(RecommendationsResource, "/recommendations")
    # Recommendations for a show (people who watched this also watched...)
    # Show recommendations (feature-flagged)
    if feature_flags.get('recommendations', True):
        api.add_resource(ShowRecommendationsResource, "/shows/<int:show_id>/recommendations")
    # Predictive seat suggestion
    api.add_resource(SeatSuggestionResource, "/shows/<int:show_id>/seat_suggestion")
    # Chatbot endpoint
    api.add_resource(ChatbotResource, "/chatbot")
    # OTP (email / sms) endpoints
    api.add_resource(SendOtpResource, "/auth/send-otp")
    api.add_resource(VerifyOtpResource, "/auth/verify-otp")
    # Offers and pricing
    api.add_resource(OffersResource, "/offers")
    api.add_resource(OfferDetailResource, "/offers/<int:offer_id>")
    api.add_resource(PricingResource, "/shows/<int:show_id>/pricing")
    api.add_resource(AnalyticsSalesResource, "/analytics/sales")
    api.add_resource(AdminStatsTimeseriesResource, "/admin/stats/timeseries")
    api.add_resource(AdminSeatImportResource, "/admin/theatres/<int:theatre_id>/seats/import")
    api.add_resource(AdminSeatExportResource, "/admin/theatres/<int:theatre_id>/seats/export")
    api.add_resource(AdminBulkShowsImportResource, "/admin/shows/import")
