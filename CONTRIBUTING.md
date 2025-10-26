# Contributing to Nur Al-Ilm

Thank you for your interest in contributing to Nur Al-Ilm! This project serves the Muslim Ummah, and contributions are a form of Sadaqah Jariyah (ongoing charity).

## Ways to Contribute

### 1. Add Maliki Fiqh Content 📚

**Easiest way**: Upload through the UI
- Click upload button
- Select image/PDF of Maliki fiqh book
- System automatically adds to knowledge base

**Via Code**: Add to `src/services/fiqh_scraper.py`
```python
{
    "topic": "Your Topic",
    "category": "salah",  # or zakat, sawm, hajj, etc.
    "text": """
    # Your Content Here
    Full Maliki fiqh text with markdown formatting
    """,
    "source": "Source Book Name",
    "references": ["Al-Risala", "Mukhtasar Khalil"],
}
```

Then run: `python scrape_and_populate_rag.py`

### 2. Improve Code 💻

**Backend (Python/FastAPI)**:
- Add new API endpoints
- Improve RAG search algorithm
- Add new external APIs
- Optimize performance

**Frontend (React/TypeScript)**:
- Enhance UI/UX
- Add new components
- Improve responsiveness
- Add accessibility features

### 3. Fix Bugs 🐛

- Check GitHub Issues
- Test and reproduce
- Fix and submit PR
- Add tests for the fix

### 4. Improve Documentation 📖

- Fix typos
- Add examples
- Translate to other languages
- Create video tutorials

---

## Development Workflow

### 1. Fork & Clone

```bash
# Fork on GitHub first
git clone https://github.com/YOUR-USERNAME/nur-al-ilm.git
cd nur-al-ilm
```

### 2. Create Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 3. Set Up Development Environment

```bash
# Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# Frontend
cd frontend
npm install
```

### 4. Make Changes

- Follow code style guidelines
- Add tests for new features
- Update documentation
- Test locally

### 5. Run Tests

```bash
# Backend tests
pytest tests/ -v --cov=src

# Frontend tests
cd frontend
npm test
```

### 6. Commit & Push

```bash
git add .
git commit -m "feat: Add new Maliki fiqh topic on inheritance"
git push origin feature/your-feature-name
```

### 7. Create Pull Request

- Go to GitHub
- Create PR from your branch
- Describe changes clearly
- Link related issues

---

## Code Style Guidelines

### Python (Backend)

**Follow PEP 8 and project conventions:**

```python
# Good ✅
async def get_prayer_times(
    latitude: float,
    longitude: float,
    method: int = 2,
) -> Optional[Dict[str, Any]]:
    """
    Get prayer times for location.
    
    Args:
        latitude: Location latitude
        longitude: Location longitude  
        method: Calculation method
    
    Returns:
        Prayer times data or None
    """
    try:
        # Implementation
        pass
    except Exception as e:
        logger.error(f"Failed to get prayer times: {e}")
        return None

# Bad ❌
def getPrayerTimes(lat,lon,m=2):
    # No types, no docstring
    pass
```

**Requirements:**
- ✅ Type hints for all functions
- ✅ Google-style docstrings
- ✅ Error handling with logging
- ✅ Async for I/O operations
- ✅ Use Pydantic for validation

### TypeScript (Frontend)

```typescript
// Good ✅
interface PrayerTimesProps {
  latitude: number;
  longitude: number;
}

export function PrayerTimesWidget({ latitude, longitude }: PrayerTimesProps) {
  const [times, setTimes] = useState<PrayerTimes | null>(null);
  // Implementation
}

// Bad ❌
export function PrayerTimesWidget(props) {
  // No types
}
```

**Requirements:**
- ✅ TypeScript for all code
- ✅ Interface definitions
- ✅ Functional components
- ✅ Proper hooks usage
- ✅ CSS classes via Tailwind

---

## Islamic Content Guidelines

### Authenticity

- ✅ **Verify sources** before adding content
- ✅ **Cite references** (book name, author)
- ✅ **Use authentic texts** (Al-Risala, Mukhtasar Khalil, etc.)
- ❌ **No personal opinions** without scholarly basis
- ❌ **No weak/fabricated** hadiths

### Language

- ✅ **Respectful tone** always
- ✅ **Accurate translations**
- ✅ **Preserve Arabic terms** with translations
- ✅ **Scholarly terminology**

### Fiqh Content

- ✅ **Clearly label madhab** positions
- ✅ **Mention differences** between madhabs
- ✅ **Provide evidence** from Quran/Hadith
- ✅ **Practical guidance** where appropriate

---

## Testing Requirements

### Backend Tests

```python
# tests/test_new_feature.py
import pytest
from src.services.your_service import YourService

class TestYourService:
    @pytest.mark.asyncio
    async def test_your_function(self):
        service = YourService()
        result = await service.your_function()
        
        assert result is not None
        assert isinstance(result, dict)
```

**Coverage**: Aim for 80%+ test coverage

### Frontend Tests

```typescript
// Not yet implemented - coming soon
```

---

## Adding New Maliki Fiqh Topics

### Step 1: Prepare Content

Format as markdown:

```markdown
# Topic Title

## Section 1
Content with proper structure...

## Maliki Position
Specific Maliki ruling...

## Evidence
Quranic verses and Hadiths...

**Source**: Al-Risala, Mukhtasar Khalil
```

### Step 2: Add to Scraper

Edit `src/services/fiqh_scraper.py`:

```python
{
    "id": "maliki_your_topic_1",
    "topic": "Your Topic Title",
    "madhab": "Maliki",
    "category": "appropriate_category",  # salah, zakat, etc.
    "text": """Your markdown content here""",
    "source": "Source Book",
    "references": ["Al-Risala", "Mukhtasar Khalil"],
}
```

### Step 3: Update RAG

```bash
python scrape_and_populate_rag.py
```

### Step 4: Test

```bash
# Search for your topic
curl -X POST http://localhost:8000/api/v1/upload/knowledge-base/search \
  -F "query=your topic keywords"

# Ask AI
curl -X POST http://localhost:8000/api/v1/ai/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Question about your topic"}'
```

---

## Commit Message Guidelines

Use conventional commits:

```
feat: Add new Maliki fiqh topic on inheritance
fix: Correct RTL alignment for Arabic lists
docs: Update API reference with new endpoints
style: Format code with ruff
test: Add tests for RAG search
refactor: Optimize vector search performance
chore: Update dependencies
```

---

## Pull Request Checklist

Before submitting:

- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
- [ ] Islamic content verified for authenticity
- [ ] Tested locally
- [ ] No sensitive data (API keys, etc.)

---

## Questions?

- Open an issue on GitHub
- Email: contribute@example.com
- Discord: [Community Server](#)

---

جزاك الله خيراً for contributing! May Allah accept it as Sadaqah Jariyah.

