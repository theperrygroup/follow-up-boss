# Follow Up Boss API Client

A comprehensive Python client library for the Follow Up Boss API, providing easy access to all Follow Up Boss endpoints with full type safety and thorough documentation.

## Features

- **Complete API Coverage**: Support for all Follow Up Boss API endpoints
- **Type Safety**: Full type hints throughout the library
- **Easy to Use**: Simple, intuitive interface
- **Well Documented**: Comprehensive docstrings and examples
- **Async Support**: Built with modern Python async/await patterns
- **Error Handling**: Robust error handling and validation
- **Extensible**: Easy to extend for custom use cases

## Installation

```bash
pip install follow-up-boss
```

## Quick Start

```python
from follow_up_boss import FollowUpBossApiClient

# Initialize the client
client = FollowUpBossApiClient(
    api_key="your_api_key",
    x_system="Your-System-Name",
    x_system_key="your_system_key"
)

# Get all people
people = client.people.get_all()

# Create a new person
new_person = client.people.create({
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "555-123-4567"
})

# Update a person
updated_person = client.people.update(person_id, {
    "name": "John Smith"
})

# Delete a person
client.people.delete(person_id)
```

## Environment Variables

You can also configure the client using environment variables:

```bash
FOLLOW_UP_BOSS_API_KEY=your_api_key
X_SYSTEM=Your-System-Name
X_SYSTEM_KEY=your_system_key
```

```python
from follow_up_boss import FollowUpBossApiClient

# Client will automatically use environment variables
client = FollowUpBossApiClient()
```

## API Resources

The client provides access to all Follow Up Boss API resources:

### Core Resources
- **People**: Manage contacts and leads
- **Deals**: Track real estate transactions ([Commission Field Guide](DEALS_COMMISSION_GUIDE.md))
- **Events**: Handle activities and interactions
- **Tasks**: Manage todo items and follow-ups
- **Notes**: Add and retrieve notes
- **Appointments**: Schedule and manage appointments

### Communication
- **Text Messages**: Send and receive SMS
- **Email Templates**: Manage email templates
- **Text Message Templates**: Manage SMS templates
- **Webhooks**: Configure webhook endpoints
- **Reactions**: Handle message reactions

### Organization
- **Teams**: Manage team structures
- **Users**: Handle user accounts
- **Groups**: Organize contacts into groups
- **Pipelines**: Manage sales pipelines
- **Stages**: Configure pipeline stages
- **Smart Lists**: Dynamic contact lists

### Configuration
- **Custom Fields**: Define custom data fields
- **Action Plans**: Automated workflow templates
- **Appointment Types**: Configure appointment categories
- **Appointment Outcomes**: Track appointment results

### Attachments & Files
- **Person Attachments**: File attachments for contacts
- **Deal Attachments**: File attachments for deals

## Deals API - Commission Fields

The Deals API includes special handling for commission fields. **Important**: Commission fields must be passed as top-level parameters, not in `custom_fields`.

```python
from follow_up_boss import Deals, DealsValidationError

deals_api = Deals(client)

# ✅ Correct - Commission fields as top-level parameters
deal = deals_api.create_deal(
    name="123 Main Street",
    stage_id=26,
    price=450000,
    commissionValue=13500.0,
    agentCommission=9450.0,
    teamCommission=4050.0
)

# ❌ Incorrect - This will raise DealsValidationError
try:
    deal = deals_api.create_deal(
        name="Deal Name",
        stage_id=26,
        custom_fields={'commissionValue': 13500}  # This fails
    )
except DealsValidationError as e:
    print(f"Validation error: {e}")
```

### Commission Helper Methods

```python
# Set commission using helper method
commission_data = {
    'total': 15000.0,
    'agent': 10500.0,
    'team': 4500.0
}

updated_deal = deals_api.set_deal_commission(deal_id, commission_data)
```

For complete commission field documentation, see the [Commission Field Guide](DEALS_COMMISSION_GUIDE.md).

## Advanced Usage

### Error Handling

```python
from follow_up_boss import FollowUpBossApiClient
from follow_up_boss.exceptions import ApiError, AuthenticationError

try:
    client = FollowUpBossApiClient(api_key="invalid_key")
    people = client.people.get_all()
except AuthenticationError:
    print("Invalid API credentials")
except ApiError as e:
    print(f"API Error: {e}")
```

### Pagination

```python
# Get all people with pagination
all_people = []
page = 1

while True:
    response = client.people.get_all(page=page, limit=100)
    people = response.get('people', [])
    
    if not people:
        break
        
    all_people.extend(people)
    page += 1
```

### Custom Headers

```python
# Add custom headers to requests
client = FollowUpBossApiClient(
    api_key="your_key",
    custom_headers={
        "X-Custom-Header": "custom_value"
    }
)
```

## Development

### Setup

```bash
git clone https://github.com/theperrygroup/follow-up-boss.git
cd follow-up-boss
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black follow_up_boss tests
isort follow_up_boss tests
```

### Type Checking

```bash
mypy follow_up_boss
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass (`pytest`)
6. Format your code (`black` and `isort`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions, issues, or feature requests, please:

1. Check the [documentation](https://github.com/theperrygroup/follow-up-boss#readme)
2. Search [existing issues](https://github.com/theperrygroup/follow-up-boss/issues)
3. Create a [new issue](https://github.com/theperrygroup/follow-up-boss/issues/new) if needed

## Changelog

### Version 0.2.0
- **Major Commission Field Improvements**: Added comprehensive commission field handling with validation
- **Enhanced Error Messages**: Context-specific error guidance for common mistakes
- **New Validation System**: `DealsValidationError` for deals-specific validation
- **Commission Helper Methods**: `set_deal_commission()` for easier commission management
- **Field Name Normalization**: Consistent field naming between requests and responses
- **Comprehensive Documentation**: New commission field guide with examples and troubleshooting
- **Enhanced Testing**: Complete test coverage for all commission field scenarios
- **Improved Developer Experience**: Better error messages, helper properties, and validation

### Version 0.1.2
- Removed appointment test log file logging

### Version 0.1.1
- Updated website URL to https://theperry.group

### Version 0.1.0
- Initial release
- Complete API coverage for all Follow Up Boss endpoints
- Full type safety with comprehensive type hints
- Comprehensive test suite
- Documentation and examples

## Related Projects

- [Follow Up Boss API Documentation](https://followupboss.com/api/)
- [Follow Up Boss](https://followupboss.com/) - The official Follow Up Boss platform

---

Made with ❤️ by [The Perry Group](https://theperry.group) 