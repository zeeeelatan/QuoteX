from app.models.korea_job_salary import KoreaJobSalary


def test_korea_job_salary_crud(client, db):
    record = KoreaJobSalary(
        city="首尔",
        position_name="桌面运维（3年+）",
        monthly_salary_krw=5640000,
        notes="测试基准岗位",
        is_active=True,
    )
    db.add(record)
    db.commit()

    response = client.get("/korea-job-salaries/options")
    assert response.status_code == 200
    assert response.json()[0]["monthly_salary_krw"] == 5640000

    record_id = response.json()[0]["id"]
    response = client.put(
        f"/korea-job-salaries/{record_id}",
        json={"monthly_salary_krw": 5800000},
    )
    assert response.status_code == 200
    assert response.json()["monthly_salary_krw"] == 5800000

    response = client.delete(f"/korea-job-salaries/{record_id}")
    assert response.status_code == 200
