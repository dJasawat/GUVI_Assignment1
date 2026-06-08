import pandas as pd
import matplotlib.pyplot as plt


def showShipmentTrends(shipmentDF):
    
     #Convert order_date to datetime
     shipmentDF["order_date"] = pd.to_datetime(shipmentDF["order_date"])
    # Count shipments per month
     monthly_trend = (
      shipmentDF
     .groupby(shipmentDF["order_date"].dt.to_period("M"))
     .size()
      )
     fig, ax = plt.subplots(figsize=(10, 5))

     ax.plot(
          monthly_trend.index.astype(str),
          monthly_trend.values,
          marker="o"
     )
        
     ax.set_title("Monthly Shipment Trends")

     ax.set_xlabel("Month")
     ax.set_ylabel("Number of Shipments")
     ax.grid(True)
 
     plt.xticks(rotation=45)
     plt.tight_layout()
     return fig

def OperationalCostChart(CostDF):
      labels=['fuel_cost','labor_cost','misc_cost']
      size= [CostDF['fuel_cost'].sum(),CostDF['labor_cost'].sum(),CostDF['misc_cost'].sum()]
      fig,ax = plt.subplots(figsize=(6,6))

      ax.pie(
            size,
            labels=labels,
            autopct='%1.1f%%'
      ) 

      return fig

def shipmentCancelationByOrigin(shipmentdf):
      fig, ax = plt.subplots(figsize=(10, 5))
  
      shipmentdf = shipmentdf.sort_values(by="shipment_count",ascending=False).head(10)
      ax.plot(shipmentdf["origin"], 
       shipmentdf["shipment_count"],
       marker="o") 
      
      ax.set_title("Top 10  origins",loc='left')

      ax.set_xlabel("Origin")
      ax.set_ylabel("Cancelled Shipments")
      ax.grid(True)

      plt.xticks(rotation=45)
      plt.tight_layout()
      return fig

def shipmentCancelationByCourier(shipmentdf):
      fig, ax = plt.subplots(figsize=(10, 5))
      shipmentdf = shipmentdf.sort_values(by="shipment_count",ascending=False).head(10)
      ax.plot(shipmentdf["name"], 
       shipmentdf["shipment_count"],
       marker="o") 
      
      ax.set_title("Top 10 Courier",loc='left')


      ax.set_xlabel("Courier ame")
      ax.set_ylabel("Cancelled Shipments")
      ax.grid(True)


      plt.xticks(rotation=45)
      plt.tight_layout()
      return fig










