"""Synthetic authenticated endpoint regressions; inference is captured, never called."""
from datetime import datetime
import pytest
from app.models.life_entry import LifeEntry
from app.models.user import User
from app.services import autobiography_service

LEVELS = ['self', 'trusted', 'heirs', 'public']
DATE = datetime(2026, 11, 21, 12)


def entry(user, visibility='self', **extra):
    return LifeEntry(user_id=user.id, time_bucket='adult',
                     timeframe_label='Synthetic', headline='fixture-' + visibility,
                     raw_text='Synthetic private text', distilled='Synthetic',
                     visibility=visibility, seal_type=extra.pop('seal_type', 'none'),
                     topic_buckets=['fixture'], **extra)


def capture(monkeypatch):
    captured = {}
    async def canned(**kwargs):
        captured.update(kwargs)
        return {'outline': {}, 'markdown': 'Synthetic output'}
    monkeypatch.setattr(autobiography_service.llm_orchestrator,
                        'generate_autobiography', canned)
    return captured


def generate(client, headers, audience, date=DATE, scope=None):
    response = client.post('/api/autobiography/generate', headers=headers,
                           json={'audience': audience, 'date': date.isoformat(),
                                 'scope': scope or {'type': 'all'}, 'tone': 'balanced'})
    assert response.status_code == 200, response.text


def headlines(captured):
    return [row['headline'] for rows in captured['grouped_entries'].values()
            for row in rows]


@pytest.mark.parametrize('audience', LEVELS)
@pytest.mark.parametrize('visibility', LEVELS)
def test_all_visibility_audience_pairs(client, db_session, test_user, auth_headers,
                                      monkeypatch, audience, visibility):
    db_session.add(entry(test_user, visibility))
    db_session.commit()
    captured = capture(monkeypatch)
    generate(client, auth_headers, audience)
    expected = ['fixture-' + visibility] if LEVELS.index(visibility) >= LEVELS.index(audience) else []
    assert headlines(captured) == expected
    assert captured['audience'] == audience


@pytest.mark.parametrize('seal,blocked,date,visible', [
    ('none', ['public'], DATE, True),
    ('until_date', ['public'], datetime(2026, 11, 21, 11), False),
    ('until_date', ['public'], DATE, True),
    ('until_date', ['public'], datetime(2026, 11, 21, 13), True),
    ('until_date', ['trusted'], datetime(2026, 11, 21, 11), True),
    ('until_event', ['public'], DATE, False),
    ('until_event', ['trusted'], DATE, True),
    ('until_manual', ['public'], DATE, False),
    ('until_manual', ['trusted'], DATE, True),
])
def test_existing_seal_date_rules(client, db_session, test_user, auth_headers,
                                  monkeypatch, seal, blocked, date, visible):
    db_session.add(entry(test_user, 'public', seal_type=seal,
                         seal_release_at=DATE, seal_audiences_blocked=blocked))
    db_session.commit()
    captured = capture(monkeypatch)
    generate(client, auth_headers, 'public', date)
    assert headlines(captured) == (['fixture-public'] if visible else [])


def test_existing_user_and_year_scope_filters(client, db_session, test_user,
                                              auth_headers, monkeypatch):
    other = User(email='other-synthetic@example.com', password_hash='not-used')
    db_session.add(other)
    db_session.flush()
    db_session.add_all([
        entry(test_user, 'public', approx_year_start=2001, approx_year_end=2002),
        entry(test_user, 'heirs', approx_year_start=1990, approx_year_end=1991),
        entry(other, 'public', approx_year_start=2001, approx_year_end=2002),
    ])
    db_session.commit()
    captured = capture(monkeypatch)
    generate(client, auth_headers, 'self', scope={'type': 'time_range', 'from': 2000, 'to': 2005})
    assert headlines(captured) == ['fixture-public']
