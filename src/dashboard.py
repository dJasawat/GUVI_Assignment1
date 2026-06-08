import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import graphes
import utils
import traceback
   
  
 
  
# ---------------- SIDEBAR ---------------- #
st.sidebar.title("Analytical Views")
option = st.sidebar.radio(
    "Navigate",
    ("Home","Shipment Search & Filtering", "Courier Performance","Cost Analytics","Cancellation")
)

try :
  
# ---------------- HOME ---------------- #
    if option == "Home":
      
        st.title("Smart Logistics Management Dashboard")
        st.markdown("Monitor shipments,couriers and financials in real time!")
        st.header("Overviews KPIs", divider="gray")
   
        #Total shipments
     
        shipmentsDF = utils.fetch_data("SELECt * FROM shipments")
        total_shipments = utils.fetch_data("SELECT count(*) as totalShipments FROM shipments")["totalShipments"]
        deliveredShipments =utils.fetch_data("select count(*) as deliveredShipments  from shipments where status ='Delivered'")["deliveredShipments"]
        deliverdShipementsPercentage = round(deliveredShipments/total_shipments*100,2)
     
        cancelledShipments = utils.fetch_data("select count(*) as cancelledShipments  from shipments where status ='Cancelled'")["cancelledShipments"]
        cancelledShipmentsPercentage = round(cancelledShipments/total_shipments*100,2)
       
        deliveryTime_df =utils.fetch_data("select DATEDIFF(delivery_date,order_date) AS deliveryDays from logistics_dataset.shipments where delivery_date is not null")["deliveryDays"]
    
        cost_df= utils.fetch_data("select *, (fuel_cost+ labor_cost+misc_cost) as total_cost from costs")

        total_cost= cost_df["total_cost"].sum()

        # avarage delivery time in days and hours
        average_hours = deliveryTime_df.mean()
        average_days = int(average_hours // 24)
        remaining_hours = round(average_hours % 24, 1)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Shipments", total_shipments)
        col2.metric("Delivered Shipments(%)", deliverdShipementsPercentage)
        col3.metric("Cancelled Shipments(%)", cancelledShipmentsPercentage)
        col4,col5,col6 =st.columns(3)
        col4.metric("Average Delivery Time(days)",  f"{average_days} days {remaining_hours} hours")
        col5.metric("Total Delivery Time(Days)",deliveryTime_df.sum())
        col6.metric("Total Operational costs",round(total_cost,2))


        # Show Shipments Trends
        st.header("Shipment Trends", divider="gray")
        fig =  graphes.showShipmentTrends(shipmentsDF)
        st.pyplot(fig)
                   

    if option== "Cost Analytics":
     # show operation Cost Chart
        st.header("Operation Cost Distribution", divider="grey")
        cost_df= utils.fetch_data("select *, (fuel_cost+ labor_cost+misc_cost) as total_cost from costs")
        fig= graphes.OperationalCostChart(cost_df)
        st.pyplot(fig)


#---------------------Shipment Search & Filtering -----------------#
    if option == "Shipment Search & Filtering":
        st.title ="Shipment Search & Filtering"
        query ="SELECT * FROM shipments"
        shipmentsDF = utils.fetch_data(query)

         # 🔹 Search box

        shipmentId = st.sidebar.text_input("Track shipment by shipment ID")
        status = st.sidebar.multiselect("Select Status", shipmentsDF["status"].drop_duplicates())

        origin = st.sidebar.selectbox("Origin" , shipmentsDF["origin"].drop_duplicates(),index=None)
        destination = st.sidebar.selectbox("destination",shipmentsDF["destination"].drop_duplicates(),index=None)
        courier_df= utils.fetch_data("Select * from courier_staff")
        courier = st.sidebar.selectbox("Courier",courier_df["name"],index=None)

        if shipmentId:
            shipment_trackingDF = utils.fetch_data(f"select * from shipment_tracking where shipment_id = '{shipmentId}'")
            st.subheader("Shipment Tracking")
            # Rename specific columns
            shipment_trackingDF = shipment_trackingDF.rename(columns={'tracking_id': 'Tracking Id', 'shipment_id': 'Shipment ID',"status" : "Status","timestamp" : "TimeStamp"})

            st.dataframe(shipment_trackingDF)

        shipmentQuery=""
        if st.sidebar.button("Submit", type="primary"):
             shipmentQuery = "SELECT s.*,c.name from shipments s  inner join  courier_staff c ON s.courier_id = c.courier_id "
             params=[]
             # filter based on status
             if status:
                placeholders = ",".join(["%s"] * len(status))

                if "where" in shipmentQuery:
                   shipmentQuery += f" AND status IN ({placeholders})"
                else:
                   shipmentQuery += f" where status IN ({placeholders})"

                params.extend(status)
           
             # filter based on origin 
             if origin:
                if 'where' in shipmentQuery:
                    shipmentQuery+= f" AND origin = %s"
                else:
                    shipmentQuery += f" where origin = %s"
                params.append(origin)

             # filter based on destination
             if destination:
                 if 'where' in shipmentQuery:
                  shipmentQuery += f" AND destination = %s"
                 else:
                   shipmentQuery += f" destination = %s"
                 params.append(destination)
             # filter based on courier
             if courier:
                courier_id = courier_df.loc[courier_df["name"] == courier,"courier_id"].iloc[0]
               
                if 'where' in shipmentQuery:
                    shipmentQuery += f" AND c.courier_id = %s"
                else:
                    shipmentQuery += f" c.courier_id = %s"
                params.append(courier_id)
                
             #Fetch data from the mysql database                  
             filteredShipment_DF = utils.fetch_data(shipmentQuery, tuple(params))
             
             if filteredShipment_DF is not None and not filteredShipment_DF.empty:
                  filteredShipment_DF = filteredShipment_DF.rename(
                                         columns={
                                               "shipment_id": "ShipmentID",
                                                "order_date": "Order Date",
                                                "origin": "Origin",
                                                "destination": "Destination",
                                                "status": "Status",
                                                "name": "Courier",
                                                "weight": "Weight",
                                                }
                                             )
                  

                  st.subheader("Filtered Shipments")
                  st.dataframe(
                  filteredShipment_DF[["ShipmentID", "Order Date", "Origin", "Destination", "Courier", "Status", "Weight"]])
             else:
                  st.warning("No shipments found.")

                                                              
    if option == "Courier Performance":
        st.header("Courier's Performance", divider="gray")
        query ="select c. name ,c.rating,c.vehicle_type, count(*) as ShipmentDelivered from courier_staff c left join shipments s on c.courier_id= s.courier_id group by c.courier_id"
        courier_shipmentsCountDF= utils.fetch_data(query)
        courier_shipmentsCountDF=courier_shipmentsCountDF.rename(columns={"n~ame":"Courier Name","rating":"Rating",'vehicle_type':"Vehicle","ShipmentDelivered":'Shipments Handled'})
        averageRating = courier_shipmentsCountDF["Rating"].mean()
        courier_shipmentsCountDF["Average Rating Comparision"] = courier_shipmentsCountDF["Rating"].apply(lambda x :"Above Average" if x >= averageRating else "Below Average")
        st.dataframe(courier_shipmentsCountDF)

    if option == "Cancellation":
        params= ['Cancelled']
        #query= "select origin, count(*) as CancelledShipments from shipments where status = %s group by origin"
        query= "select * from shipments where status = %s"
        st.header("Cancellation of shipments by origin" ,divider="grey")
        cancelledShipment_df = utils.fetch_data(query,tuple(params))

        #Bar chart to show cancelled shipments by origin
        cancelledShipmentByOrigin_df= cancelledShipment_df.groupby('origin').size().reset_index(name="shipment_count") 
        
        #st.dataframe(cancelledShipmentByOrigin_df)
        fig = graphes.shipmentCancelationByOrigin(cancelledShipmentByOrigin_df)
        st.pyplot(fig)
        
        #Bar chart to show cancelled shipments by courier
        st.header("Cancellation of shipments by Courier" ,divider="grey")
        cancelledShipmentByCourier_df= cancelledShipment_df.groupby('courier_id').size().reset_index(name="shipment_count") 
        courierStaff_df = utils.fetch_data("select * from courier_staff")
        shippmentsWithCourierName = pd.merge(cancelledShipmentByCourier_df, courierStaff_df, on="courier_id", how="inner")
        fig = graphes.shipmentCancelationByCourier(shippmentsWithCourierName)
        st.pyplot(fig)
       # st.dataframe(shippmentsWithCourierName)

    if option == "Delivery Performance Insights":
        st.header("Delivery Performance", divider="gray")
except Exception as e:
   #st.error(f"Error loading data: {e}")
    st.exception(e)
    st.code(traceback.format_exc())
   
   
   
   

   
   
    
