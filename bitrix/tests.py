import unittest
from unittest.mock import patch, MagicMock
import os
import uuid
from benchmark import Item, get_driver, scrape_product_details, main, log_directory


class TestItem(unittest.TestCase):
    """
    Unit tests for the Item class.
    """

    def test_item_initialization(self):
        """
        Test the initialization of an Item object.
        """
        title = "Test Title"
        description = "Test Description"
        price = "$10.00"
        link = "http://example.com"
        bonanza_id = "12345"
        color = "Red"
        size = "M"

        item = Item(title, description, price, link, bonanza_id, color, size)

        self.assertEqual(item.title, title)
        self.assertEqual(item.description, description)
        self.assertEqual(item.price, price)
        self.assertEqual(item.link, link)
        self.assertEqual(item.bonanza_id, bonanza_id)
        self.assertEqual(item.color, color)
        self.assertEqual(item.size, size)
        self.assertTrue(isinstance(uuid.UUID(item.unique_key, version=4), uuid.UUID))


class TestScraping(unittest.TestCase):
    """
    Unit tests for the scraping functions.
    """

    @patch('benchmark.webdriver.Chrome')
    def test_get_driver(self, MockWebDriver):
        """
        Test the get_driver function to ensure it creates a WebDriver instance and navigates to the given URL.
        """
        mock_driver = MagicMock()
        MockWebDriver.return_value = mock_driver

        driver = get_driver("http://example.com")

        MockWebDriver.assert_called_once()
        mock_driver.get.assert_called_once_with("http://example.com")
        self.assertEqual(driver, mock_driver)

    @patch('benchmark.get_driver')
    @patch('benchmark.webdriver.Chrome')
    def test_scrape_product_details(self, MockWebDriver, mock_get_driver):
        """
        Test the scrape_product_details function with a mocked product page containing an iframe for the description.
        """
        mock_driver = MagicMock()
        mock_get_driver.return_value = mock_driver
        mock_driver.find_element.side_effect = [
            MagicMock(text="Test Title"),
            MagicMock(text="$10.00"),
            MagicMock(text="12345"),
            MagicMock(text="Red"),
            MagicMock(text="M"),
            MagicMock(find_element=MagicMock(
                return_value=MagicMock(get_attribute=MagicMock(return_value="http://example.com/iframe")))),
            # html_description
            MagicMock(text="Test Description")  # description in iframe
        ]

        item_details = scrape_product_details("http://example.com/item")

        expected_details = {
            'title': "Test Title",
            'description': "Test Description",
            'price': "$10.00",
            'link': "http://example.com/item",
            'unique_key': item_details['unique_key'],
            # unique_key is randomly generated, so we just check its existence
            'bonanza_id': "12345",
            'color': "Red",
            'size': "M"
        }

        self.assertEqual(item_details, expected_details)

    @patch('benchmark.get_driver')
    @patch('benchmark.webdriver.Chrome')
    def test_scrape_product_details_no_iframe(self, MockWebDriver, mock_get_driver):
        """
        Test the scrape_product_details function with a mocked product page without an iframe for the description.
        """
        mock_driver = MagicMock()
        mock_get_driver.return_value = mock_driver
        mock_driver.find_element.side_effect = [
            MagicMock(text="Test Title"),
            MagicMock(text="$10.00"),
            MagicMock(text="12345"),
            MagicMock(text="Red"),
            MagicMock(text="M"),
            None,  # no html_description
            MagicMock(text="Test Description")  # plain_text_description
        ]

        item_details = scrape_product_details("http://example.com/item")

        expected_details = {
            'title': "Test Title",
            'description': "Test Description",
            'price': "$10.00",
            'link': "http://example.com/item",
            'unique_key': item_details['unique_key'],
            'bonanza_id': "12345",
            'color': "Red",
            'size': "M"
        }

        self.assertEqual(item_details, expected_details)


class TestMainFunction(unittest.TestCase):
    """
    Unit tests for the main function.
    """

    @patch('benchmark.get_driver')
    @patch('benchmark.scrape_product_details')
    def test_main_function(self, mock_scrape_product_details, mock_get_driver):
        """
        Test the main function to ensure it correctly scrapes items from the categories, calls the to_csv method to save the results, and logs the output.
        """
        mock_driver = MagicMock()
        mock_get_driver.return_value = mock_driver
        mock_driver.find_elements.return_value = [MagicMock(find_element=MagicMock(
            return_value=MagicMock(get_attribute=MagicMock(return_value="http://example.com/item")))) for _ in range(5)]

        mock_scrape_product_details.return_value = {
            'title': "Test Title",
            'description': "Test Description",
            'price': "$10.00",
            'link': "http://example.com/item",
            'unique_key': str(uuid.uuid4()),
            'bonanza_id': "12345",
            'color': "Red",
            'size': "M"
        }

        with patch('benchmark.pd.DataFrame.to_csv') as mock_to_csv:
            main()
            mock_to_csv.assert_called_once()

        expected_log_file = os.path.join(log_directory, 'scraping.log')
        self.assertTrue(os.path.exists(expected_log_file))


if __name__ == '__main__':
    unittest.main()
