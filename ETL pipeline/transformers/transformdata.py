import pandas as pd
if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def transform(data, *args, **kwargs):
    data['lpep_pickup_datetime'] = pd.to_datetime(data['lpep_pickup_datetime'])
    data['lpep_dropoff_datetime'] = pd.to_datetime(data['lpep_dropoff_datetime'])
    data = data[(data['passenger_count'] > 0) & (data['trip_distance'] > 0)]

    DimDate = data[['lpep_pickup_datetime','lpep_dropoff_datetime']]
    DimDate['Date_key'] = DimDate.drop_duplicates
    DimDate['Pick_hour'] = DimDate['lpep_pickup_datetime'].dt.hour
    DimDate['Pick_day'] = DimDate['lpep_pickup_datetime'].dt.day
    DimDate['Pick_month'] = DimDate['lpep_pickup_datetime'].dt.month
    DimDate['Pick_year'] = DimDate['lpep_pickup_datetime'].dt.year
    DimDate['Pick_weekday'] = DimDate['lpep_pickup_datetime'].dt.weekday
    DimDate['drop_hour'] = DimDate['lpep_dropoff_datetime'].dt.hour
    DimDate['drop_day'] = DimDate['lpep_dropoff_datetime'].dt.day
    DimDate['drop_month'] = DimDate['lpep_dropoff_datetime'].dt.month
    DimDate['drop_year'] = DimDate['lpep_dropoff_datetime'].dt.year
    DimDate['drop_weekday'] = DimDate['lpep_dropoff_datetime'].dt.weekday
    DimDate['Date_key'] = DimDate.index

    rate_mapping = {
    1: 'Standard rate',
    2: 'JFK',
    3: 'Newark',
    4: 'Nassau or Westchester',
    5: 'Negotiated fare',
    6: 'Group ride'
    }
    rate_df = pd.DataFrame(rate_mapping.items(), columns=['RatecodeID', 'Rate'])

    rate_table = pd.merge(rate_df, data[['RatecodeID']], on='RatecodeID', how='inner').drop_duplicates()

    Payment_mapping = {
    1: 'Credit card',
    2: 'Cash',
    3: 'No charge',
    4: 'Dispute',
    5: 'Unknown',
    6: 'Voided trip'
    }
    payment_df = pd.DataFrame.from_dict(Payment_mapping, orient='index', columns=['Payment_type'])
    payment_df.index.name = 'Payment_ID'
    payment_df.reset_index(inplace=True)

    Trip_type_mapping = {
    1: 'Street-hail',
    2: 'Dispatch'
    }
    Trip_type_df = pd.DataFrame.from_dict(Trip_type_mapping, orient='index', columns=['type'])
    Trip_type_df.index.name = 'Trip_type_ID'
    Trip_type_df.reset_index(inplace=True)

    data = data.rename(columns={'VendorID':'Vendor_ID','store_and_fwd_flag':'Store_Forward_fwd__flag','RatecodeID':'RateCode_ID',
                                            'PULocationID':'PuLocation_ID','DOLocationID':'DoLocation_ID','RatecodeID':'RateCode_ID',
                                            'payment_type':'Payment_ID','trip_type':'Trip_type_id'})

    Fact_table = data.merge(DimDate,on=['lpep_pickup_datetime','lpep_dropoff_datetime'])
    Fact_table['RateCode_ID'] = Fact_table['RateCode_ID'].astype(int)
    Fact_table['Payment_ID'] = Fact_table['Payment_ID'].astype(int)
    Fact_table = Fact_table.dropna(subset=['Trip_type_id'])
    Fact_table['Trip_type_id'] = Fact_table['Trip_type_id'].astype(int)
    Fact_table['Trip_type_id'] = Fact_table['Trip_type_id'].fillna(0).astype(int)



    Fact_table = Fact_table[['Vendor_ID','Date_key','PuLocation_ID','DoLocation_ID','RateCode_ID','Payment_ID','Trip_type_id','Store_Forward_fwd__flag','extra','fare_amount','mta_tax','tip_amount', 'tolls_amount','total_amount']]
    return rate_table


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
