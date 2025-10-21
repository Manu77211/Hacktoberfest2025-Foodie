import json
import datetime
import random
from collections import defaultdict
import logging

class FoodDeliverySystem:
    """
    A comprehensive food delivery management system.
    """

    def __init__(self, data_file='food_delivery_data.json'):
        """
        Initialize the food delivery system.

        Args:
            data_file (str): File to store system data.
        """
        self.data_file = data_file
        self.restaurants = {}
        self.customers = {}
        self.orders = {}
        self.delivery_agents = {}

        # Setup logging
        logging.basicConfig(
            filename='food_delivery.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        self.load_data()

    def load_data(self):
        """
        Load system data from file.
        """
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.restaurants = data.get('restaurants', {})
                self.customers = data.get('customers', {})
                self.orders = data.get('orders', {})
                self.delivery_agents = data.get('delivery_agents', {})
            self.logger.info("Data loaded successfully.")
        except FileNotFoundError:
            self.logger.info("Data file not found. Starting with empty data.")
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")

    def save_data(self):
        """
        Save system data to file.
        """
        data = {
            'restaurants': self.restaurants,
            'customers': self.customers,
            'orders': self.orders,
            'delivery_agents': self.delivery_agents
        }
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            self.logger.info("Data saved successfully.")
        except Exception as e:
            self.logger.error(f"Error saving data: {e}")

    def add_restaurant(self, name, cuisine, location, menu=None):
        """
        Add a new restaurant to the system.

        Args:
            name (str): Restaurant name.
            cuisine (str): Type of cuisine.
            location (str): Restaurant location.
            menu (dict): Restaurant menu.
        """
        restaurant_id = f"rest_{len(self.restaurants) + 1}"
        self.restaurants[restaurant_id] = {
            'name': name,
            'cuisine': cuisine,
            'location': location,
            'menu': menu or {},
            'rating': 0.0,
            'total_orders': 0
        }
        self.logger.info(f"Restaurant added: {name}")
        self.save_data()

    def add_menu_item(self, restaurant_id, item_name, price, description, category):
        """
        Add an item to a restaurant's menu.

        Args:
            restaurant_id (str): Restaurant ID.
            item_name (str): Item name.
            price (float): Item price.
            description (str): Item description.
            category (str): Item category.
        """
        if restaurant_id in self.restaurants:
            item_id = f"item_{len(self.restaurants[restaurant_id]['menu']) + 1}"
            self.restaurants[restaurant_id]['menu'][item_id] = {
                'name': item_name,
                'price': price,
                'description': description,
                'category': category,
                'available': True
            }
            self.logger.info(f"Menu item added: {item_name} to {restaurant_id}")
            self.save_data()
        else:
            self.logger.error(f"Restaurant {restaurant_id} not found.")

    def register_customer(self, name, email, phone, address):
        """
        Register a new customer.

        Args:
            name (str): Customer name.
            email (str): Customer email.
            phone (str): Customer phone.
            address (str): Customer address.
        """
        customer_id = f"cust_{len(self.customers) + 1}"
        self.customers[customer_id] = {
            'name': name,
            'email': email,
            'phone': phone,
            'address': address,
            'order_history': []
        }
        self.logger.info(f"Customer registered: {name}")
        self.save_data()
        return customer_id

    def add_delivery_agent(self, name, phone, vehicle_type):
        """
        Add a delivery agent.

        Args:
            name (str): Agent name.
            phone (str): Agent phone.
            vehicle_type (str): Type of vehicle.
        """
        agent_id = f"agent_{len(self.delivery_agents) + 1}"
        self.delivery_agents[agent_id] = {
            'name': name,
            'phone': phone,
            'vehicle_type': vehicle_type,
            'status': 'available',
            'current_order': None,
            'total_deliveries': 0
        }
        self.logger.info(f"Delivery agent added: {name}")
        self.save_data()

    def place_order(self, customer_id, restaurant_id, items, delivery_address=None):
        """
        Place a new order.

        Args:
            customer_id (str): Customer ID.
            restaurant_id (str): Restaurant ID.
            items (list): List of item IDs and quantities.
            delivery_address (str): Delivery address.

        Returns:
            str: Order ID.
        """
        if customer_id not in self.customers:
            self.logger.error(f"Customer {customer_id} not found.")
            return None

        if restaurant_id not in self.restaurants:
            self.logger.error(f"Restaurant {restaurant_id} not found.")
            return None

        order_id = f"order_{len(self.orders) + 1}"
        order_items = []
        total_price = 0

        for item_id, quantity in items:
            if item_id in self.restaurants[restaurant_id]['menu']:
                item = self.restaurants[restaurant_id]['menu'][item_id]
                if item['available']:
                    order_items.append({
                        'item_id': item_id,
                        'name': item['name'],
                        'price': item['price'],
                        'quantity': quantity
                    })
                    total_price += item['price'] * quantity
                else:
                    self.logger.warning(f"Item {item_id} is not available.")
            else:
                self.logger.error(f"Item {item_id} not found in menu.")

        if not order_items:
            self.logger.error("No valid items in order.")
            return None

        # Add delivery fee
        delivery_fee = 2.99
        total_price += delivery_fee

        order = {
            'order_id': order_id,
            'customer_id': customer_id,
            'restaurant_id': restaurant_id,
            'items': order_items,
            'total_price': round(total_price, 2),
            'status': 'placed',
            'order_time': datetime.datetime.now().isoformat(),
            'delivery_address': delivery_address or self.customers[customer_id]['address'],
            'delivery_agent': None,
            'estimated_delivery': None
        }

        self.orders[order_id] = order
        self.customers[customer_id]['order_history'].append(order_id)
        self.restaurants[restaurant_id]['total_orders'] += 1

        self.logger.info(f"Order placed: {order_id}")
        self.save_data()
        return order_id

    def assign_delivery_agent(self, order_id):
        """
        Assign a delivery agent to an order.

        Args:
            order_id (str): Order ID.
        """
        if order_id not in self.orders:
            self.logger.error(f"Order {order_id} not found.")
            return

        available_agents = [agent for agent in self.delivery_agents.values()
                           if agent['status'] == 'available']

        if available_agents:
            agent = random.choice(available_agents)
            agent_id = [k for k, v in self.delivery_agents.items() if v == agent][0]

            self.orders[order_id]['delivery_agent'] = agent_id
            self.orders[order_id]['status'] = 'assigned'
            self.delivery_agents[agent_id]['status'] = 'busy'
            self.delivery_agents[agent_id]['current_order'] = order_id

            # Estimate delivery time (15-45 minutes)
            delivery_time = datetime.datetime.now() + datetime.timedelta(minutes=random.randint(15, 45))
            self.orders[order_id]['estimated_delivery'] = delivery_time.isoformat()

            self.logger.info(f"Delivery agent {agent_id} assigned to order {order_id}")
            self.save_data()
        else:
            self.logger.warning("No available delivery agents.")

    def update_order_status(self, order_id, status):
        """
        Update the status of an order.

        Args:
            order_id (str): Order ID.
            status (str): New status.
        """
        if order_id in self.orders:
            old_status = self.orders[order_id]['status']
            self.orders[order_id]['status'] = status

            if status == 'delivered':
                agent_id = self.orders[order_id]['delivery_agent']
                if agent_id:
                    self.delivery_agents[agent_id]['status'] = 'available'
                    self.delivery_agents[agent_id]['current_order'] = None
                    self.delivery_agents[agent_id]['total_deliveries'] += 1

            self.logger.info(f"Order {order_id} status updated: {old_status} -> {status}")
            self.save_data()
        else:
            self.logger.error(f"Order {order_id} not found.")

    def get_order_status(self, order_id):
        """
        Get the current status of an order.

        Args:
            order_id (str): Order ID.

        Returns:
            dict: Order status information.
        """
        if order_id in self.orders:
            order = self.orders[order_id]
            return {
                'order_id': order_id,
                'status': order['status'],
                'order_time': order['order_time'],
                'estimated_delivery': order['estimated_delivery'],
                'total_price': order['total_price']
            }
        else:
            return None

    def generate_report(self):
        """
        Generate a system report.

        Returns:
            dict: Report data.
        """
        total_orders = len(self.orders)
        total_customers = len(self.customers)
        total_restaurants = len(self.restaurants)
        total_agents = len(self.delivery_agents)

        order_status_counts = defaultdict(int)
        for order in self.orders.values():
            order_status_counts[order['status']] += 1

        revenue = sum(order['total_price'] for order in self.orders.values()
                     if order['status'] == 'delivered')

        report = {
            'total_orders': total_orders,
            'total_customers': total_customers,
            'total_restaurants': total_restaurants,
            'total_delivery_agents': total_agents,
            'order_status_breakdown': dict(order_status_counts),
            'total_revenue': round(revenue, 2),
            'generated_at': datetime.datetime.now().isoformat()
        }

        return report

    def search_restaurants(self, cuisine=None, location=None):
        """
        Search for restaurants by cuisine or location.

        Args:
            cuisine (str): Cuisine type.
            location (str): Location.

        Returns:
            list: List of matching restaurants.
        """
        results = []
        for rest_id, restaurant in self.restaurants.items():
            if (cuisine and cuisine.lower() in restaurant['cuisine'].lower()) or \
               (location and location.lower() in restaurant['location'].lower()) or \
               (not cuisine and not location):
                results.append({
                    'id': rest_id,
                    'name': restaurant['name'],
                    'cuisine': restaurant['cuisine'],
                    'location': restaurant['location'],
                    'rating': restaurant['rating']
                })

        return results

def main():
    """
    Main function demonstrating the food delivery system.
    """
    system = FoodDeliverySystem()

    # Add sample data
    system.add_restaurant("Pizza Palace", "Italian", "Downtown")
    system.add_menu_item("rest_1", "Margherita Pizza", 12.99, "Classic cheese pizza", "Pizza")
    system.add_menu_item("rest_1", "Pepperoni Pizza", 14.99, "Pizza with pepperoni", "Pizza")

    customer_id = system.register_customer("John Doe", "john@example.com", "123-456-7890", "123 Main St")
    system.add_delivery_agent("Mike Johnson", "987-654-3210", "Bike")

    # Place an order
    order_id = system.place_order(customer_id, "rest_1", [("item_1", 2), ("item_2", 1)])
    if order_id:
        print(f"Order placed: {order_id}")

        # Assign delivery agent
        system.assign_delivery_agent(order_id)

        # Check order status
        status = system.get_order_status(order_id)
        print(f"Order status: {status}")

        # Update order status
        system.update_order_status(order_id, "out_for_delivery")
        system.update_order_status(order_id, "delivered")

    # Generate report
    report = system.generate_report()
    print("System Report:")
    print(json.dumps(report, indent=2))

    # Search restaurants
    italian_restaurants = system.search_restaurants(cuisine="Italian")
    print("Italian Restaurants:")
    for rest in italian_restaurants:
        print(f"- {rest['name']} in {rest['location']}")

if __name__ == "__main__":
    main()
