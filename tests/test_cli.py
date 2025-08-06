# this_file: tests/test_cli.py
"""Tests for CLI commands."""

import json
from unittest.mock import AsyncMock, Mock, mock_open, patch

import pytest
from rich.console import Console

from virginia_clemm_poe.__main__ import Cli
from virginia_clemm_poe.models import Architecture, BotInfo, PoeModel, Pricing, PricingDetails


class TestCliSetup:
    """Test CLI setup command."""

    def setup_method(self) -> None:
        """Setup before each test."""
        self.cli = Cli()
        self.console_mock = Mock(spec=Console)

    @patch("virginia_clemm_poe.__main__.BrowserManager.setup_chrome", new_callable=AsyncMock)
    @patch("virginia_clemm_poe.__main__.configure_logger")
    @patch("virginia_clemm_poe.__main__.console", new_callable=Mock)
    def test_setup_success(self, mock_console, mock_logger, mock_setup_chrome):
        """Test successful browser setup."""
        # Mock successful browser setup
        mock_setup_chrome.return_value = True

        # Run the command
        self.cli.setup(verbose=False)

        # Verify logging was configured
        mock_logger.assert_called_once_with(False)

        # Verify setup was called
        mock_setup_chrome.assert_called_once()

        # Verify console messages (should be called at least once, exact order may vary)
        mock_console.print.assert_any_call("[bold blue]Setting up browser for Virginia Clemm Poe...[/bold blue]")
        mock_console.print.assert_any_call("[green]✓ Chrome is available![/green]")

    @patch("virginia_clemm_poe.__main__.BrowserManager.setup_chrome", new_callable=AsyncMock)
    @patch("virginia_clemm_poe.__main__.sys.exit")
    @patch("virginia_clemm_poe.__main__.configure_logger")
    @patch("virginia_clemm_poe.__main__.console", new_callable=Mock)
    def test_setup_failure(self, mock_console, mock_logger, mock_exit, mock_setup_chrome):
        """Test browser setup failure."""
        # Mock failed browser setup
        mock_setup_chrome.return_value = False

        # Run the command
        self.cli.setup(verbose=True)

        # Verify logging was configured with verbose=True
        mock_logger.assert_called_once_with(True)

        # Verify setup was called
        mock_setup_chrome.assert_called_once()

        # Verify console messages and exit
        mock_console.print.assert_any_call("[bold blue]Setting up browser for Virginia Clemm Poe...[/bold blue]")
        mock_console.print.assert_any_call("[red]✗ Failed to set up Chrome[/red]")
        mock_exit.assert_called_once_with(1)


class TestCliStatus:
    """Test CLI status command."""

    def setup_method(self) -> None:
        """Setup before each test."""
        self.cli = Cli()

    @patch("virginia_clemm_poe.__main__.DATA_FILE_PATH")
    @patch("virginia_clemm_poe.__main__.configure_logger")
    @patch("virginia_clemm_poe.__main__.console", new_callable=Mock)
    def test_status_no_data_file(self, mock_console, mock_logger, mock_data_path):
        """Test status when no data file exists."""
        mock_data_path.exists.return_value = False

        self.cli.status(verbose=False)

        mock_logger.assert_called_once_with(False)
        mock_console.print.assert_any_call("[red]✗ No model data found[/red]")

    @patch("virginia_clemm_poe.__main__.DATA_FILE_PATH")
    @patch("virginia_clemm_poe.__main__.api.get_all_models")
    @patch("virginia_clemm_poe.__main__.configure_logger")
    @patch("virginia_clemm_poe.__main__.console", new_callable=Mock)
    def test_status_with_data(self, mock_console, mock_logger, mock_get_models, mock_data_path):
        """Test status with existing data file."""
        # Mock data file exists
        mock_data_path.exists.return_value = True

        # Mock file content
        mock_data = {
            "models": [
                {"id": "test-model", "pricing": {"details": {}}},
                {"id": "test-model-2", "bot_info": {"creator": "@test"}},
            ]
        }

        # Mock sample model with pricing
        sample_model = PoeModel(
            id="test-model",
            object="model",
            created=1704369600,
            owned_by="testorg",
            permission=[],
            root="test-model",
            architecture=Architecture(input_modalities=["text"], output_modalities=["text"], modality="text->text"),
            pricing=Pricing(checked_at="2025-08-04T12:00:00Z", details=PricingDetails()),
        )

        mock_get_models.return_value = [sample_model]

        with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
            self.cli.status(verbose=True)

        mock_logger.assert_called_once_with(True)
        mock_console.print.assert_any_call("[green]✓ Model data found[/green]")


class TestCliUpdate:
    """Test CLI update command."""

    def setup_method(self) -> None:
        """Setup before each test."""
        self.cli = Cli()

    @patch("virginia_clemm_poe.__main__.os.environ.get")
    @patch("virginia_clemm_poe.__main__.sys.exit")
    @patch("virginia_clemm_poe.__main__.configure_logger")
    @patch("virginia_clemm_poe.__main__.console", new_callable=Mock)
    def test_update_no_api_key(self, mock_console, mock_logger, mock_exit, mock_env_get):
        """Test update command without API key."""
        mock_env_get.return_value = None  # No API key
        # Make sys.exit actually stop execution by raising SystemExit
        mock_exit.side_effect = SystemExit(1)

        # The method should call sys.exit(1), which we're mocking to raise SystemExit
        with pytest.raises(SystemExit):
            self.cli.update()

        # Verify logging was configured
        mock_logger.assert_called_once_with(False)
        # Check that the error message was printed
        mock_console.print.assert_any_call("[red]✗ POE_API_KEY not set[/red]")
        mock_exit.assert_called_once_with(1)

    @patch("virginia_clemm_poe.__main__.ModelUpdater")
    @patch("virginia_clemm_poe.__main__.os.environ.get")
    @patch("virginia_clemm_poe.__main__.configure_logger")
    @patch("virginia_clemm_poe.__main__.console", new_callable=Mock)
    def test_update_with_api_key(self, mock_console, mock_logger, mock_env_get, mock_updater_class):
        """Test successful update with API key."""
        mock_env_get.return_value = "test-api-key"
        mock_updater = Mock()
        mock_updater.update_all = AsyncMock()
        mock_updater_class.return_value = mock_updater

        self.cli.update(all=True, force=False, verbose=False)

        mock_logger.assert_called_once_with(False)
        mock_updater_class.assert_called_once_with("test-api-key", debug_port=9222, verbose=False)
        # Verify the updater's update_all method was called
        mock_updater.update_all.assert_called_once_with(force=False, update_info=True, update_pricing=True)

    @patch("virginia_clemm_poe.__main__.console", new_callable=Mock)
    def test_update_no_mode_selected(self, mock_console):
        """Test update with no update mode selected."""
        # This tests the _determine_update_mode method
        result = self.cli._determine_update_mode(info=False, pricing=False, all=False)

        assert result == (False, False)

    def test_update_mode_selection(self):
        """Test different update mode selections."""
        # Test --all mode (default)
        result = self.cli._determine_update_mode(info=False, pricing=False, all=True)
        assert result == (True, True)

        # Test --info only
        result = self.cli._determine_update_mode(info=True, pricing=False, all=True)
        assert result == (True, False)  # all should be disabled

        # Test --pricing only
        result = self.cli._determine_update_mode(info=False, pricing=True, all=True)
        assert result == (False, True)  # all should be disabled


class TestCliSearch:
    """Test CLI search command."""

    def setup_method(self) -> None:
        """Setup before each test."""
        self.cli = Cli()

    @patch("virginia_clemm_poe.__main__.DATA_FILE_PATH")
    @patch("virginia_clemm_poe.__main__.configure_logger")
    @patch("virginia_clemm_poe.__main__.console", new_callable=Mock)
    def test_search_no_data(self, mock_console, mock_logger, mock_data_path):
        """Test search when no data file exists."""
        mock_data_path.exists.return_value = False

        self.cli.search("test-query")

        mock_console.print.assert_any_call(
            "[yellow]No model data found. Run 'virginia-clemm-poe update' first.[/yellow]"
        )

    @patch("virginia_clemm_poe.__main__.api.search_models")
    @patch("virginia_clemm_poe.__main__.DATA_FILE_PATH")
    @patch("virginia_clemm_poe.__main__.configure_logger")
    @patch("virginia_clemm_poe.__main__.console", new_callable=Mock)
    def test_search_no_results(self, mock_console, mock_logger, mock_data_path, mock_search):
        """Test search with no matching results."""
        mock_data_path.exists.return_value = True
        mock_search.return_value = []

        self.cli.search("nonexistent-model")

        mock_console.print.assert_any_call("[yellow]No models found matching 'nonexistent-model'[/yellow]")

    @patch("virginia_clemm_poe.__main__.api.search_models")
    @patch("virginia_clemm_poe.__main__.DATA_FILE_PATH")
    @patch("virginia_clemm_poe.__main__.configure_logger")
    @patch("virginia_clemm_poe.__main__.console", new_callable=Mock)
    def test_search_with_results(self, mock_console, mock_logger, mock_data_path, mock_search):
        """Test search with matching results."""
        mock_data_path.exists.return_value = True

        # Mock search results
        sample_model = PoeModel(
            id="test-model-1",
            object="model",
            created=1704369600,
            owned_by="testorg",
            permission=[],
            root="test-model-1",
            architecture=Architecture(input_modalities=["text"], output_modalities=["text"], modality="text->text"),
            pricing=Pricing(
                checked_at="2025-08-04T12:00:00Z", details=PricingDetails(input_text="10 points/1k tokens")
            ),
            bot_info=BotInfo(creator="@testcreator"),
        )

        mock_search.return_value = [sample_model]

        self.cli.search("test", show_pricing=True, show_bot_info=True)

        mock_search.assert_called_once_with("test")
        mock_console.print.assert_any_call("[green]Found 1 models[/green]")

    def test_format_pricing_info(self):
        """Test pricing information formatting."""
        # Test model with pricing
        sample_model = PoeModel(
            id="test-model",
            object="model",
            created=1704369600,
            owned_by="testorg",
            permission=[],
            root="test-model",
            architecture=Architecture(input_modalities=["text"], output_modalities=["text"], modality="text->text"),
            pricing=Pricing(
                checked_at="2025-08-04T12:00:00Z",
                details=PricingDetails(input_text="10 points/1k tokens", initial_points_cost="100 points"),
            ),
        )

        pricing_info, updated = self.cli._format_pricing_info(sample_model)

        assert "100 points" in pricing_info
        assert "10 points/1k tokens" in pricing_info
        assert updated == "2025-08-04"

        # Test model with pricing error
        error_model = PoeModel(
            id="error-model",
            object="model",
            created=1704369600,
            owned_by="testorg",
            permission=[],
            root="error-model",
            architecture=Architecture(input_modalities=["text"], output_modalities=["text"], modality="text->text"),
            pricing_error="Failed to scrape",
        )

        pricing_info, updated = self.cli._format_pricing_info(error_model)

        assert "Error: Failed to scrape" in pricing_info
        assert updated == "-"


class TestCliList:
    """Test CLI list command."""

    def setup_method(self) -> None:
        """Setup before each test."""
        self.cli = Cli()

    @patch("virginia_clemm_poe.__main__.DATA_FILE_PATH")
    @patch("virginia_clemm_poe.__main__.configure_logger")
    @patch("virginia_clemm_poe.__main__.console", new_callable=Mock)
    def test_list_no_data(self, mock_console, mock_logger, mock_data_path):
        """Test list when no data file exists."""
        mock_data_path.exists.return_value = False

        self.cli.list()

        mock_console.print.assert_any_call(
            "[yellow]No model data found. Run 'virginia-clemm-poe update' first.[/yellow]"
        )

    @patch("virginia_clemm_poe.__main__.api.get_all_models")
    @patch("virginia_clemm_poe.__main__.api.get_models_with_pricing")
    @patch("virginia_clemm_poe.__main__.DATA_FILE_PATH")
    @patch("virginia_clemm_poe.__main__.configure_logger")
    @patch("virginia_clemm_poe.__main__.console", new_callable=Mock)
    def test_list_with_data(self, mock_console, mock_logger, mock_data_path, mock_get_with_pricing, mock_get_all):
        """Test list with data available."""
        mock_data_path.exists.return_value = True

        # Mock models
        sample_model = PoeModel(
            id="test-model-1",
            object="model",
            created=1704369600,
            owned_by="testorg",
            permission=[],
            root="test-model-1",
            architecture=Architecture(input_modalities=["text"], output_modalities=["text"], modality="text->text"),
            pricing=Pricing(checked_at="2025-08-04T12:00:00Z", details=PricingDetails()),
        )

        mock_get_all.return_value = [sample_model]
        mock_get_with_pricing.return_value = [sample_model]

        self.cli.list(with_pricing=False, limit=10)

        mock_get_all.assert_called()
        # Should display summary and model list
        assert mock_console.print.call_count >= 2


class TestCliClearCache:
    """Test CLI clear cache command."""

    def setup_method(self) -> None:
        """Setup before each test."""
        self.cli = Cli()

    @patch("virginia_clemm_poe.__main__.DATA_FILE_PATH")
    @patch("virginia_clemm_poe.__main__.configure_logger")
    @patch("virginia_clemm_poe.__main__.console", new_callable=Mock)
    def test_clear_cache_data_only(self, mock_console, mock_logger, mock_data_path):
        """Test clearing data cache only."""
        mock_data_path.exists.return_value = True
        mock_data_path.unlink = Mock()

        self.cli.clear_cache(data=True, browser=False, all=False)

        mock_data_path.unlink.assert_called_once()
        mock_console.print.assert_any_call("[green]✓ Model data cleared[/green]")

    @patch("virginia_clemm_poe.__main__.DATA_FILE_PATH")
    @patch("virginia_clemm_poe.__main__.shutil.rmtree")
    @patch("virginia_clemm_poe.__main__.configure_logger")
    @patch("virginia_clemm_poe.__main__.console", new_callable=Mock)
    def test_clear_cache_browser_only(self, mock_console, mock_logger, mock_rmtree, mock_data_path):
        """Test clearing browser cache only."""
        mock_install_path = Mock()
        mock_install_path.exists.return_value = True

        # Mock the import and install_dir function
        with patch("virginia_clemm_poe.__main__.shutil.rmtree") as mock_rmtree:
            with patch("playwrightauthor.utils.paths.install_dir", return_value=mock_install_path):
                self.cli.clear_cache(data=False, browser=True, all=False)

                mock_rmtree.assert_called_once_with(mock_install_path)
                mock_console.print.assert_any_call("[green]✓ Browser cache cleared[/green]")

    @patch("virginia_clemm_poe.__main__.configure_logger")
    @patch("virginia_clemm_poe.__main__.console", new_callable=Mock)
    def test_clear_cache_no_selection(self, mock_console, mock_logger):
        """Test clear cache with no selection."""
        self.cli.clear_cache(data=False, browser=False, all=False)

        mock_console.print.assert_any_call("[yellow]No cache type selected.[/yellow]")


class TestCliDoctor:
    """Test CLI doctor command."""

    def setup_method(self) -> None:
        """Setup before each test."""
        self.cli = Cli()

    @patch("virginia_clemm_poe.__main__.configure_logger")
    @patch("virginia_clemm_poe.__main__.console", new_callable=Mock)
    def test_doctor_command(self, mock_console, mock_logger):
        """Test doctor diagnostic command."""
        # Mock all the individual check methods
        self.cli._check_python_version = Mock(return_value=0)
        self.cli._check_api_key = Mock(return_value=0)
        self.cli._check_browser = Mock(return_value=0)
        self.cli._check_network = Mock(return_value=0)
        self.cli._check_dependencies = Mock(return_value=0)
        self.cli._check_data_file = Mock(return_value=0)
        self.cli._display_summary = Mock()

        self.cli.doctor(verbose=True)

        # Verify all checks were called
        self.cli._check_python_version.assert_called_once()
        self.cli._check_api_key.assert_called_once()
        self.cli._check_browser.assert_called_once()
        self.cli._check_network.assert_called_once()
        self.cli._check_dependencies.assert_called_once()
        self.cli._check_data_file.assert_called_once()
        self.cli._display_summary.assert_called_once_with(0)

    def test_check_python_version(self):
        """Test Python version check."""
        with patch("sys.version_info", (3, 12, 0)):
            result = self.cli._check_python_version()
            assert result == 0

        with patch("sys.version_info", (3, 11, 0)):
            result = self.cli._check_python_version()
            assert result == 1

    @patch("virginia_clemm_poe.__main__.os.environ.get")
    def test_check_api_key(self, mock_env_get):
        """Test API key check."""
        # Test missing API key
        mock_env_get.return_value = None
        result = self.cli._check_api_key()
        assert result == 1

        # Test API key present
        mock_env_get.return_value = "test-api-key"
        with patch("httpx.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            result = self.cli._check_api_key()
            assert result == 0


class TestCliValidation:
    """Test CLI validation methods."""

    def setup_method(self) -> None:
        """Setup before each test."""
        self.cli = Cli()

    @patch("virginia_clemm_poe.__main__.os.environ.get")
    @patch("virginia_clemm_poe.__main__.sys.exit")
    @patch("virginia_clemm_poe.__main__.console", new_callable=Mock)
    def test_validate_api_key_missing(self, mock_console, mock_exit, mock_env_get):
        """Test API key validation when missing."""
        mock_env_get.return_value = None

        self.cli._validate_api_key(None)

        mock_exit.assert_called_once_with(1)
        mock_console.print.assert_any_call("[red]✗ POE_API_KEY not set[/red]")

    @patch("virginia_clemm_poe.__main__.os.environ.get")
    def test_validate_api_key_present(self, mock_env_get):
        """Test API key validation when present."""
        mock_env_get.return_value = "test-api-key"

        result = self.cli._validate_api_key(None)

        assert result == "test-api-key"

    def test_validate_api_key_override(self):
        """Test API key validation with override."""
        result = self.cli._validate_api_key("override-key")

        assert result == "override-key"

    @patch("virginia_clemm_poe.__main__.DATA_FILE_PATH")
    @patch("virginia_clemm_poe.__main__.console", new_callable=Mock)
    def test_validate_data_exists(self, mock_console, mock_data_path):
        """Test data existence validation."""
        # Test when data doesn't exist
        mock_data_path.exists.return_value = False
        result = self.cli._validate_data_exists()
        assert result is False

        # Test when data exists
        mock_data_path.exists.return_value = True
        result = self.cli._validate_data_exists()
        assert result is True
