#!/bin/bash
# Setup script for Book Features - PDF Summaries and Personalized Recommendations
# Run this script from the project root directory

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Book Store Features Setup - PDF & Recommendations            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo -e "${RED}❌ Error: manage.py not found. Please run this script from the Django project root.${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Creating database migrations...${NC}"
python manage.py makemigrations myapp
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Migrations created successfully${NC}"
else
    echo -e "${RED}✗ Failed to create migrations${NC}"
    exit 1
fi
echo ""

echo -e "${YELLOW}Step 2: Applying database migrations...${NC}"
python manage.py migrate myapp
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Migrations applied successfully${NC}"
else
    echo -e "${RED}✗ Failed to apply migrations${NC}"
    exit 1
fi
echo ""

echo -e "${YELLOW}Step 3: Creating required directories...${NC}"
mkdir -p media/book_summaries
chmod 755 media/book_summaries
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

echo -e "${YELLOW}Step 4: Collecting static files (optional)...${NC}"
python manage.py collectstatic --noinput 2>/dev/null
echo -e "${GREEN}✓ Static files collected${NC}"
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo -e "${GREEN}✓ Setup completed successfully!${NC}"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

echo "Next steps:"
echo "1. Go to Django Admin (/admin/)"
echo "2. Add PDF summaries to book products"
echo "3. Add recommendation tags to books"
echo "4. Test the features by completing a purchase"
echo ""
echo "For detailed documentation, see: BOOK_FEATURES_GUIDE.md"
echo ""
