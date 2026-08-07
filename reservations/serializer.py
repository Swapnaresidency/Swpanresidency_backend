from rest_framework import serializers
from .models import CheckIn, CheckOut  # <-- Fixed: Added CheckOut import here

class CheckInSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(
        source="customer.customer_name", 
        read_only=True
    )
    mobile_no = serializers.CharField(
        source="customer.mobile_no", 
        read_only=True
    )
    room_no = serializers.CharField(
        source="room.room_no", 
        read_only=True
    )
    
    # Grab the price from the related room instance dynamically
    base_daily_rent = serializers.SerializerMethodField()
    
    # Provide a reliable formatted string that handles date + time
    formatted_checkin = serializers.SerializerMethodField()

    class Meta:
        model = CheckIn
        fields = '__all__'

    def get_base_daily_rent(self, obj):
        if obj.room and hasattr(obj.room, 'room_type') and obj.room.room_type:
            return float(obj.room.room_type.rent)
        elif obj.room and hasattr(obj.room, 'rent'):
            return float(obj.room.rent)
        return 0.0

    def get_formatted_checkin(self, obj):
        date_str = str(obj.checkin_date)
        time_str = str(obj.checkin_time)[:5] if hasattr(obj, 'checkin_time') else "00:00"
        return f"{date_str} @ {time_str}"

class CheckOutSerializer(serializers.ModelSerializer):
    # Traverses the relationships: CheckOut -> CheckIn -> Customer/Room
    customer_name = serializers.ReadOnlyField(source='checkin.customer.customer_name')
    room_no = serializers.ReadOnlyField(source='checkin.room.room_no')
    total_amount = serializers.ReadOnlyField(source='checkin.total_amount')

    class Meta:
        model = CheckOut
        fields = '__all__'