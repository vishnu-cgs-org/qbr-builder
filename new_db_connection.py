import pandas as pd
import logging

# Set up logging
logger = logging.getLogger(__name__)

def load_data_from_csv(csv_path, filter_column='Partner_ID', filter_value=None):
    """Load data from a CSV file, apply a filter, and clean the 'Est. Renewal Available' column."""
    try:
        df = pd.read_csv(csv_path)
        logger.info(f"Data loaded successfully from {csv_path}.")
        logger.info(f"Data contains {df.shape[0]} rows and {df.shape[1]} columns.")
        
        # Apply filter if filter_value is provided
        if filter_value:
            original_size = df.shape[0]
            df = df[df[filter_column] == filter_value]
            filtered_size = df.shape[0]
            logger.info(f"Filtered data on {filter_column}={filter_value}. "
                        f"Rows reduced from {original_size} to {filtered_size}.")
        
        # Clean up 'Est. Renewal Available' column
        if 'Est. Renewal Available' in df.columns:
            df['Est. Renewal Available'] = (
                df['Est. Renewal Available']
                .replace({',': ''}, regex=True)  # Remove commas
                .fillna(0)                        # Fill NaNs with 0
                .astype(int)                      # Convert to integer
            )
            logger.info("'Est. Renewal Available' column cleaned: commas removed, NaNs filled, and converted to int.")
        else:
            logger.warning("'Est. Renewal Available' column not found in the dataset.")
        
        return df
    except Exception as e:
        logger.error(f"Failed to load data from {csv_path}. Error: {e}")
        return None


def create_pivot_table(df, index_col, value_col, agg_func):
    """Generate a pivot table based on index and value columns."""
    try:
        # Pivot table with specified aggregation function
        pivot_table = pd.pivot_table(
            df,
            index=index_col,
            values=value_col,
            aggfunc=agg_func
        )
        logger.info(f"Pivot table generated with shape: {pivot_table.shape}")
        return pivot_table.sort_values(by=value_col, ascending=False).head(5)
    except Exception as e:
        logger.error(f"Failed to generate pivot table. Error: {e}")
        return None


if __name__ == "__main__":
    # Path to your CSV file
    csv_path = "resources/sample_data_for_qbr_builder.csv"
    
    # Load the data from CSV
    data_df = load_data_from_csv(csv_path)
    
    if data_df is not None:
        # Define the columns for each pivot table
        index_column_1 = 'FY FQ'      # Pivot table 1: Fiscal Quarter as index
        value_column_1 = 'Opp #'      # Count unique opportunities
        agg_func_1 = lambda x: len(x.unique()) # Unique count
        
        index_column_2 = 'Opp Stage'          # Pivot table 2: Partner ID as index
        value_column_2 = 'Est. Renewal Available'      # Sum of Total ACV
        agg_func_2 = 'sum'                     # Summing the values

        index_column_3 = 'Product Group Detail'              # Pivot table 3: Region as index
        value_column_3 = 'Opp #'      # Count unique opportunities by region
        agg_func_3 = lambda x: len(x.unique()) # Unique count

        # Generate the first pivot table: unique count of opportunities by fiscal quarter
        pivot_table_1 = create_pivot_table(data_df, index_column_1, value_column_1, agg_func_1)
        
        # Generate the second pivot table: sum of Total ACV by partner ID
        pivot_table_2 = create_pivot_table(data_df, index_column_2, value_column_2, agg_func_2)
        
        # Generate the third pivot table: unique count of opportunities by region
        pivot_table_3 = create_pivot_table(data_df, index_column_3, value_column_3, agg_func_3)
        
        # Display the pivot tables
        if pivot_table_1 is not None:
            print("\nPivot Table 1: Unique count of opportunities by fiscal quarter")
            print(pivot_table_1)
        
        if pivot_table_2 is not None:
            print("\nPivot Table 2: Sum of Total ACV by Opp Stage")
            print(pivot_table_2)
        
        if pivot_table_3 is not None:
            print("\nPivot Table 3: Unique count of opportunities by Product")
            print(pivot_table_3)
