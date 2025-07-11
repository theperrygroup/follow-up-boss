# Follow Up Boss Deals API - Commission Field Guide

## Overview
This guide explains how to properly handle commission fields when working with the Follow Up Boss Deals API. Based on real-world implementation experience, this documentation addresses common issues and provides best practices for commission field handling.

## 🚨 Critical Information

### Commission Field Handling
**Important**: Commission fields cannot be passed via `custom_fields` parameter in `create_deal()` or `update_deal()` methods. They must be passed as top-level parameters.

#### ❌ Incorrect Usage
```python
# This fails silently - commission fields are ignored
deals_api.create_deal(
    name="Deal Name",
    stage_id=26,
    price=450000,
    custom_fields={
        'commissionValue': 13500,
        'agentCommission': 9450,
        'teamCommission': 4050
    }
)
```

#### ✅ Correct Usage
```python
# This works - commission fields as top-level parameters
deals_api.create_deal(
    name="Deal Name",
    stage_id=26,
    price=450000,
    commissionValue=13500,
    agentCommission=9450,
    teamCommission=4050
)
```

## Commission Fields Reference

### Supported Commission Fields
- `commissionValue` (float): Total commission amount
- `agentCommission` (float): Agent's commission portion  
- `teamCommission` (float): Team's commission portion

### Data Types
All commission fields accept float values. The API will automatically convert integers to floats.

### Field Validation
The library now includes validation that will raise a `DealsValidationError` if commission fields are found in `custom_fields`:

```python
from follow_up_boss import DealsValidationError

try:
    deal = deals_api.create_deal(
        name="Deal Name",
        stage_id=26,
        custom_fields={'commissionValue': 13500}  # This will raise an error
    )
except DealsValidationError as e:
    print(f"Validation error: {e}")
    # Output: Validation error: 'commissionValue' should be a top-level parameter, not in custom_fields.
```

## Complete Deal Creation Examples

### Example 1: Basic Deal with Commission
```python
deal = deals_api.create_deal(
    name="123 Main Street",                    # Required: Deal name
    stage_id=26,                               # Required: Pipeline stage ID
    price=450000,                              # Optional: Deal price
    commissionValue=13500.0,                   # Optional: Total commission
    agentCommission=9450.0,                    # Optional: Agent commission
    teamCommission=4050.0                      # Optional: Team commission
)

print(f"Deal created with ID: {deal['id']}")
print(f"Commission set: {deal.get('has_commission', False)}")
```

### Example 2: Complete Deal with All Fields
```python
deal = deals_api.create_deal(
    name="456 Oak Avenue",
    stage_id=26,
    price=675000,
    projectedCloseDate="2025-08-10",          # Expected close date
    status="Active",                           # Deal status
    description="Luxury home with pool",      # Deal description
    commissionValue=20250.0,                   # Total commission (3% of price)
    agentCommission=14175.0,                   # Agent commission (70% of total)
    teamCommission=6075.0                      # Team commission (30% of total)
)
```

### Example 3: Using the Commission Helper Method
```python
# Create deal first
deal = deals_api.create_deal(
    name="789 Pine Street",
    stage_id=26,
    price=525000
)

# Set commission using helper method
commission_data = {
    'total': 15750.0,
    'agent': 11025.0,
    'team': 4725.0
}

updated_deal = deals_api.set_deal_commission(deal['id'], commission_data)
print(f"Commission updated: {updated_deal.get('has_commission', False)}")
```

## Commission Updates

### Updating Commission on Existing Deals
```python
# Update commission on existing deal
commission_update = {
    'commissionValue': 15000.0,
    'agentCommission': 10500.0,
    'teamCommission': 4500.0
}

updated_deal = deals_api.update_deal(deal_id, commission_update)
```

### Using the Helper Method
```python
# Alternative approach using the helper method
commission_data = {
    'total': 15000.0,
    'agent': 10500.0,
    'team': 4500.0
}

updated_deal = deals_api.set_deal_commission(deal_id, commission_data)
```

## Field Name Mapping

### API Request vs Response Field Names
The API sometimes uses different field names in requests vs responses:

| Request Field | Response Field | Description |
|---------------|----------------|-------------|
| `close_date` | `projectedCloseDate` | Expected close date |
| `commission` | `commissionValue` | Total commission amount |
| `user_id` | `userId` | User ID |
| `person_id` | `personId` | Person ID |
| `stage_id` | `stageId` | Stage ID |
| `pipeline_id` | `pipelineId` | Pipeline ID |

### Field Name Normalization
The library provides field name normalization for consistent handling:

```python
# Retrieve deal with normalized field names
deal = deals_api.retrieve_deal(deal_id, normalize_fields=True)

# This converts response field names to consistent format
# projectedCloseDate -> close_date
# commissionValue -> commission
# etc.
```

## Error Handling

### Enhanced Error Messages
The library now provides enhanced error messages for common mistakes:

```python
try:
    deal = deals_api.create_deal(
        name="Deal Name",
        stage_id=26,
        custom_fields={'commissionValue': 13500}
    )
except DealsValidationError as e:
    print(e)
    # Output includes helpful guidance about commission field usage
```

### Common Error Scenarios

#### 1. Commission Fields in Custom Fields
```python
# This will raise DealsValidationError
try:
    deal = deals_api.create_deal(
        name="Deal Name",
        stage_id=26,
        custom_fields={
            'commissionValue': 13500,
            'agentCommission': 9450
        }
    )
except DealsValidationError as e:
    print(f"Error: {e}")
    # The error message will list all problematic fields and provide correction guidance
```

#### 2. Missing Required Fields
```python
# This will raise FollowUpBossApiException with enhanced error message
try:
    deal = deals_api.create_deal(
        name="Deal Name"
        # Missing required stage_id
    )
except FollowUpBossApiException as e:
    print(f"API Error: {e}")
    # Enhanced error message includes guidance about required fields
```

## Response Enhancements

### Helper Properties
The library adds helpful properties to deal responses:

```python
deal = deals_api.create_deal(
    name="Deal Name",
    stage_id=26,
    commissionValue=13500.0
)

# Helper properties added to response
print(f"Has commission: {deal['has_commission']}")           # True/False
print(f"Total people: {deal['total_people']}")              # Count of associated people
print(f"Total users: {deal['total_users']}")                # Count of associated users
```

## Best Practices

### 1. Always Use Top-Level Parameters for Commission
```python
# ✅ Correct
deal = deals_api.create_deal(
    name="Deal Name",
    stage_id=26,
    commissionValue=13500.0
)

# ❌ Incorrect
deal = deals_api.create_deal(
    name="Deal Name",
    stage_id=26,
    custom_fields={'commissionValue': 13500.0}
)
```

### 2. Use Helper Methods for Complex Operations
```python
# ✅ Use helper method for commission updates
commission_data = {
    'total': 15000.0,
    'agent': 10500.0,
    'team': 4500.0
}
deals_api.set_deal_commission(deal_id, commission_data)

# ❌ Manual field construction
deals_api.update_deal(deal_id, {
    'commissionValue': 15000.0,
    'agentCommission': 10500.0,
    'teamCommission': 4500.0
})
```

### 3. Handle Validation Errors Appropriately
```python
try:
    deal = deals_api.create_deal(**deal_data)
except DealsValidationError as e:
    # Handle validation errors specifically
    logger.error(f"Deal validation failed: {e}")
    # Provide user-friendly error message
    return {"error": "Commission fields must be top-level parameters"}
except FollowUpBossApiException as e:
    # Handle API errors
    logger.error(f"API error: {e}")
    return {"error": "Failed to create deal"}
```

### 4. Use Field Normalization When Needed
```python
# When you need consistent field names
deal = deals_api.retrieve_deal(deal_id, normalize_fields=True)

# When you want raw API response
deal = deals_api.retrieve_deal(deal_id, normalize_fields=False)
```

## Migration Guide

### If You're Currently Using Custom Fields for Commission

1. **Identify Problem Code**:
   ```python
   # Find code like this
   deals_api.create_deal(
       name="Deal",
       stage_id=26,
       custom_fields={'commissionValue': 13500}
   )
   ```

2. **Update to Top-Level Parameters**:
   ```python
   # Change to this
   deals_api.create_deal(
       name="Deal",
       stage_id=26,
       commissionValue=13500
   )
   ```

3. **Add Error Handling**:
   ```python
   from follow_up_boss import DealsValidationError
   
   try:
       deal = deals_api.create_deal(
           name="Deal",
           stage_id=26,
           commissionValue=13500
       )
   except DealsValidationError as e:
       # Handle validation errors
       logger.error(f"Validation error: {e}")
   ```

## Testing Commission Fields

### Unit Tests
```python
def test_commission_fields():
    """Test commission field handling."""
    deal = deals_api.create_deal(
        name="Test Deal",
        stage_id=26,
        commissionValue=13500,
        agentCommission=9450,
        teamCommission=4050
    )
    
    assert deal['commissionValue'] == 13500
    assert deal['agentCommission'] == 9450
    assert deal['teamCommission'] == 4050
    assert deal['has_commission'] is True
```

### Integration Tests
```python
def test_commission_update_flow():
    """Test the complete commission update flow."""
    # Create deal
    deal = deals_api.create_deal(name="Test Deal", stage_id=26)
    
    # Set commission
    commission_data = {
        'total': 15000.0,
        'agent': 10500.0,
        'team': 4500.0
    }
    
    updated_deal = deals_api.set_deal_commission(deal['id'], commission_data)
    
    # Verify commission was set
    assert updated_deal['commissionValue'] == 15000.0
    assert updated_deal['has_commission'] is True
```

## Troubleshooting

### Common Issues and Solutions

**Q: My commission fields aren't showing up in the deal**
A: Commission fields must be passed as top-level parameters, not in `custom_fields`. Update your code to use `commissionValue=13500` instead of `custom_fields={'commissionValue': 13500}`.

**Q: I'm getting a DealsValidationError**
A: This means you're trying to pass commission fields in `custom_fields`. Move them to top-level parameters. The error message will provide specific guidance.

**Q: What's the difference between commission and commissionValue?**
A: Use `commissionValue` for API requests. The response may contain both field names for backwards compatibility.

**Q: How do I associate clients and agents with a deal?**
A: Use the `update_deal()` method with `peopleIds` and `userIds` parameters after creating the deal:

```python
# Create deal first
deal = deals_api.create_deal(name="Deal Name", stage_id=26)

# Associate people and users
deals_api.update_deal(deal['id'], {
    'peopleIds': [person1_id, person2_id],    # Associate clients
    'userIds': [agent_user_id]                # Associate agent
})
```

## API Reference

### DealsValidationError
Custom exception raised when commission fields are found in `custom_fields`.

```python
class DealsValidationError(Exception):
    """Exception raised for deals-specific validation errors."""
    pass
```

### Enhanced Methods

#### create_deal()
```python
def create_deal(
    self,
    name: str,
    stage_id: int,
    # ... other parameters
    commissionValue: Optional[float] = None,
    agentCommission: Optional[float] = None,
    teamCommission: Optional[float] = None,
    **kwargs: Any
) -> Union[Dict[str, Any], str]:
```

#### set_deal_commission()
```python
def set_deal_commission(
    self, 
    deal_id: int, 
    commission_data: Dict[str, float]
) -> Union[Dict[str, Any], str]:
```

#### retrieve_deal()
```python
def retrieve_deal(
    self, 
    deal_id: int, 
    normalize_fields: bool = False
) -> Dict[str, Any]:
```

---

*This guide was created based on real-world implementation experience with the Follow Up Boss API. Last updated: January 2025* 