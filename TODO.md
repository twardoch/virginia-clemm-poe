# this_file: TODO.md

# Virginia Clemm Poe - Development Tasks

## ✅ Phase 9: Dual Pricing Model Support (COMPLETED 2025-10-15)

### 9.1 Data Model Refactoring
- [x] Analyze new API pricing format
- [x] Design unified pricing model architecture
- [x] **Create new pricing model classes**
  - [x] Implement `ApiPricing` model for dollar-based pricing
  - [x] Rename `PricingDetails` to `ScrapedPricingDetails`
  - [x] Rename `Pricing` to `ScrapedPricing`
  - [x] Create `UnifiedPricing` container model
  - [x] Add display methods for unified output
- [x] **Update PoeBot class**
  - [x] Replace `pricing: Pricing` with `pricing: UnifiedPricing`
  - [x] Update `has_pricing()` method for new structure
  - [x] Update `needs_pricing_update()` logic
  - [x] Update `get_primary_cost()` for dual sources
- [x] **Implement data migration**
  - [x] Create migration function for existing data
  - [x] Add version field to JSON format
  - [x] Implement backward compatibility loader
  - [x] Test migration with production data

### 9.2 Updater Refactoring
- [x] **API pricing integration**
  - [x] Parse API pricing into `ApiPricing` model
  - [x] Handle null/missing pricing fields
  - [x] Convert string prices to Decimal
  - [x] Store API pricing in unified model
- [x] **Scraping updates**
  - [x] Update scraping to use `ScrapedPricing`
  - [x] Preserve existing scraping logic
  - [x] Update error handling for new structure
  - [x] Handle list values for pricing fields (e.g., mixed dollar/point values)
- [x] **Merge strategy**
  - [x] Implement dual-source update logic
  - [x] Preserve existing scraped data during API updates
  - [x] Add force-scrape flag support
  - [x] Optimize parallel processing

### 9.3 CLI Display Updates
- [x] **Unified pricing display**
  - [x] Implement `display_primary()` method
  - [x] Implement `display_full()` method
  - [x] Add smart formatting logic
  - [x] Handle missing pricing gracefully
- [x] **Search command updates**
  - [x] Show API pricing by default
  - [x] Add option to show scraped pricing
  - [x] Update table formatting
- [x] **List command updates**
  - [x] Display dual pricing in list view
  - [x] Add pricing format filter
  - [x] Update sorting logic
- [x] **New CLI options**
  - [x] Add `--pricing-format` flag (api/scraped/both)
  - [x] Add `--show-details` for detailed view
  - [x] Update help text and documentation

### 9.4 Testing & Validation
- [x] **Unit tests**
  - [x] Test new pricing models (25 comprehensive tests)
  - [x] Test migration logic
  - [x] Test display formatting
  - [x] Test backward compatibility
  - [x] Test list value handling for scraped fields
- [x] **Integration tests**
  - [x] Test full update cycle
  - [x] Test API + scraping combination
  - [x] Test CLI commands
  - [x] Test data persistence
- [x] **Performance tests**
  - [x] Benchmark update speed
  - [x] Check memory usage
  - [x] Validate cache efficiency

### 9.5 Documentation & Release
- [x] **Documentation updates**
  - [x] Update API documentation in docstrings
  - [x] Update CLI help text
  - [x] Create migration guide in WORK.md
  - [x] Update README examples (via CLI help)
- [x] **Release preparation**
  - [x] Update CHANGELOG.md
  - [x] Create backup of production data (auto-handled)
  - [x] Test on staging environment
  - [x] Prepare rollback plan (version field enables rollback)

## ✅ Completed Phases

### Phase 7: Balance API & Browser Stability ✅ (2025-08-06)
- ✅ Fixed browser error dialogs
- ✅ Implemented GraphQL balance retrieval
- ✅ Enhanced cookie extraction
- ✅ Added retry logic and fallback chain

### Phase 6: Recent Fixes ✅
- ✅ Balance command with automatic browser fallback
- ✅ 5-minute balance cache implementation
- ✅ Fixed status command showing 0 models
- ✅ Merged doctor functionality into status command

### Phase 5: PlaywrightAuthor Integration ✅
- ✅ Chrome for Testing exclusive support
- ✅ Session reuse workflow
- ✅ Pre-authorized sessions
- ✅ Documentation updates

### Phases 1-4: Core Development ✅
- ✅ Initial package structure
- ✅ API integration
- ✅ Web scraping implementation
- ✅ CLI interface
- ✅ Data persistence
- ✅ Performance optimization
- ✅ Enterprise-grade documentation

## 🚧 Phase 10: Quality & Reliability Improvements (IN PROGRESS)

### 10.1 Code Cleanup Tasks (Priority: HIGH)
- [x] **Remove Commented-Out Code**: Clean up ERA001 violations ✅ (2025-10-15)
  - Files already cleaned up by linter
  - Valid `# this_file:` comments preserved
  - Test files properly formatted
- [x] **Fix Import Organization**: Resolve PLC0415 violations ✅ (2025-10-15)
  - Conditional imports in utils/paths.py are intentional (soft dependency pattern)
  - Platform-specific imports kept as-is for fallback handling
  - This is a good pattern for optional dependencies
- [x] **Replace Bare Except Blocks**: Fix E722 and improve error handling specificity ✅ (2025-10-15)
  - Fixed bare except in debug_login.py
  - All exceptions now use `except Exception:` or specific types
  - Error handling properly structured

### 10.2 Data Integrity & Validation (Priority: MEDIUM)
- [ ] **Add JSON Schema Validation**: Implement schema validation for poe_bots.json
  - Create JSON schema for bot data structure
  - Validate on load and before save
  - Add schema migration support for future changes
- [ ] **Implement Data Consistency Checks**: Add validation for model data
  - Verify pricing data consistency (api vs scraped)
  - Check for required fields in bot info
  - Validate timestamp formats and ranges
- [ ] **Add Model ID Validation**: Strengthen input validation in CLI
  - Validate model IDs exist before operations
  - Add fuzzy matching for user-friendly search
  - Provide "did you mean?" suggestions for typos

### 10.3 Performance & Reliability (Priority: MEDIUM)
- [ ] **Optimize Browser Pool Management**: Improve connection reuse
  - Add connection warm-up for faster first request
  - Implement connection health metrics
  - Add automatic pool size adjustment based on load
- [ ] **Enhance Cache Hit Rate**: Improve caching effectiveness
  - Add cache preloading for common queries
  - Implement cache compression for memory efficiency
  - Add cache statistics to status command
- [ ] **Add Progress Indicators**: Improve user feedback during long operations
  - Add progress bars for bulk updates
  - Show ETA for scraping operations
  - Add verbose mode with detailed operation status

## 🔮 Future Enhancements (Phase 11+)

### Advanced Pricing Analytics
- [ ] Historical pricing tracking
- [ ] Trend analysis and visualization
- [ ] Cost optimization recommendations
- [ ] Price-performance analysis
- [ ] Usage-based cost projections

### Enhanced Data Export
- [ ] Export both pricing formats
- [ ] Custom export templates
- [ ] Pricing comparison reports
- [ ] Bulk pricing updates via CSV
- [ ] API endpoint for programmatic access

### Real-time Updates
- [ ] Webhook support for pricing changes
- [ ] Automatic background updates
- [ ] Price change notifications
- [ ] Alert thresholds configuration
- [ ] Subscription management

### Enterprise Features
- [ ] Multi-user support
- [ ] Role-based access control
- [ ] Audit logging
- [ ] Compliance reporting
- [ ] SLA monitoring

## Quick Reference

### Current Sprint (Week 1: 2025-10-15 to 2025-10-22)
Focus: Data model refactoring and migration
- Implement new pricing models
- Create migration logic
- Update PoeBot class
- Begin updater refactoring

### Next Sprint (Week 2: 2025-10-23 to 2025-10-29)
Focus: Integration and CLI updates
- Complete updater refactoring
- Update all CLI commands
- Implement display logic
- Comprehensive testing

### Final Sprint (Week 3: 2025-10-30 to 2025-11-05)
Focus: Polish and release
- Performance optimization
- Documentation updates
- User migration guide
- Production release