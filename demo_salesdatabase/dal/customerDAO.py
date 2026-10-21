from demo_salesdatabase.connectors.connector import Connector

class customerDAO:
    @staticmethod
    def getCustomer():
        sql = """
            SELECT DISTINCT
                customer.CustomerID,
                Age,
                Annual_Income,
                Spending_Score
            FROM customer, customer_spend_score
            WHERE customer.CustomerID = customer_spend_score.CustomerID;
        """

        conn = Connector()
        conn.connect()
        df = conn.queryDataset(sql)
        return df