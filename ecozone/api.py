from datetime import datetime
from typing import List, Optional

from ninja import NinjaAPI, Schema

from .models import TimeseriesRedispatch


api = NinjaAPI(title="ECO zone API")


@api.get("/timeseries/redispatch", response=List[list])
def get_timeseries_redispatch(
    request, start: Optional[datetime] = None, end: Optional[datetime] = None
):
    return TimeseriesRedispatch.objects.get_timeseries_data(start, end)
