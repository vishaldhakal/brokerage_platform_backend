# Projects API - Lots Management

## Overview

The lots management system has been refactored to follow proper REST API patterns with individual lot endpoints instead of handling lots through project updates.

## API Endpoints

### Project-Specific Lot Operations

#### Get Project Lots
```
GET /api/projects/{project_slug}/lots/
```
Returns all lots for a specific project.

#### Create New Lot
```
POST /api/projects/{project_slug}/lots/
```
Creates a new lot for a specific project.

**Request Body:**
```json
{
  "lot_number": "A1",
  "availability_status": "Available",
  "lot_size": "5000.00",
  "price": "250000.00",
  "est_completion": "Spring 2024",
  "floor_plan_ids": [1, 2, 3]
}
```

#### Update Existing Lot
```
PUT /api/projects/{project_slug}/lots/{lot_id}/
```
Updates an existing lot.

**Request Body:** Same as create, but can include partial updates.

#### Delete Lot
```
DELETE /api/projects/{project_slug}/lots/{lot_id}/
```
Deletes a specific lot.

### Global Lot Operations (Admin)

#### Get All Lots
```
GET /api/lots/
```
Returns all lots across all projects (with filtering).

#### Get Specific Lot
```
GET /api/lots/{lot_id}/
```
Returns a specific lot by ID.

## Data Structure

### Lot Model
```python
class Lot(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    lot_number = models.CharField(max_length=50)
    availability_status = models.CharField(max_length=20, choices=AVAILABILITY_STATUS_CHOICES)
    lot_size = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    est_completion = models.CharField(max_length=100, blank=True)
    lot_rendering = models.FileField(upload_to='lot_renderings/', blank=True)
    floor_plans = models.ManyToManyField(FloorPlan, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Availability Status Choices
- Available
- Reserved
- Sold
- Under Construction
- Coming Soon

## File Uploads

### Lot Rendering
- Supported formats: Images (JPG, PNG, GIF, WebP)
- Upload via multipart form data
- File field name: `lot_rendering`

### Example with File Upload
```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -F "lot_number=A1" \
  -F "availability_status=Available" \
  -F "lot_size=5000.00" \
  -F "price=250000.00" \
  -F "est_completion=Spring 2024" \
  -F "floor_plan_ids=[1,2,3]" \
  -F "lot_rendering=@/path/to/image.jpg" \
  http://localhost:8000/api/projects/{project_slug}/lots/
```

## Benefits of New Structure

1. **Proper REST API Design**: Each lot has its own resource endpoint
2. **Individual Operations**: Create, read, update, delete operations are atomic
3. **Better Error Handling**: Specific error responses for lot operations
4. **Improved Performance**: No need to send entire project data for lot changes
5. **Cleaner Code**: Separation of concerns between project and lot management
6. **Better Testing**: Individual endpoints are easier to test
7. **Scalability**: Can handle large numbers of lots without affecting project updates

## Migration Notes

- Old project update endpoints no longer handle lots
- Frontend must use new lot-specific endpoints
- Existing lot data remains intact
- Project serializer still includes lots as read-only data for display purposes

## Frontend Integration

The frontend should now:
1. Use `/api/projects/{slug}/lots/` for CRUD operations
2. Handle file uploads through multipart form data
3. Implement proper error handling for individual operations
4. Use optimistic updates for better UX
