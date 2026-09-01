import os
from pathlib import Path

import pytest

from backend.vision.vlm_client import (
    GroqVLMClient,
)


@pytest.mark.integration
def test_groq_vision():

    if not os.getenv("VLM_API_KEY"):
        pytest.skip(
            "VLM_API_KEY not configured"
        )

    image = Path(
        "data/processed/rendered/page_0001.png"
    )

    if not image.exists():
        pytest.skip(
            "Rendered invoice image not found"
        )

    client = GroqVLMClient()

    result = client.extract(
        document_text="Financial invoice",
        image_path=image,
    )

    assert isinstance(
        result,
        dict,
    )

    assert "vendor_name" in result

    assert "total_amount" in result

    assert "line_items" in result