use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct Task {
    pub id: u64,
    pub title: String,
}

#[derive(Debug, Deserialize)]
pub struct CreateTaskInput {
    pub title: String,
}

/// 核心商業邏輯：驗證任務標題
pub fn validate_task_title(title: &str) -> Result<String, &'static str> {
    let trimmed = title.trim();
    if trimmed.is_empty() {
        return Err("標題不能為空");
    }
    if trimmed.chars().count() > 50 {
        return Err("標題長度不能超過 50 個字元");
    }
    Ok(trimmed.to_string())
}

// ========================================================
// 測試 1：Server 單元測試 (Unit Test)
// 專注測試核心函式與邊界邏輯，不依賴網路或伺服器環境
// ========================================================
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_validate_title_success() {
        let input = "  完成自動化測試  ";
        let result = validate_task_title(input);
        assert_eq!(result, Ok("完成自動化測試".to_string()));
    }

    #[test]
    fn test_validate_title_empty() {
        assert_eq!(validate_task_title(""), Err("標題不能為空"));
        assert_eq!(validate_task_title("   "), Err("標題不能為空"));
    }

    #[test]
    fn test_validate_title_too_long() {
        let long_title = "a".repeat(51);
        assert_eq!(
            validate_task_title(&long_title),
            Err("標題長度不能超過 50 個字元")
        );
    }
}