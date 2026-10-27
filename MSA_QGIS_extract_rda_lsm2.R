# Get arguments from command line/python
args <- commandArgs(trailingOnly = TRUE)
save_directory <- (args[[1]])
file_name_data <- args[[2]]
file_name_fallspeed <- file.path(save_directory, "temp_fallspeeds.csv")
file_name_lookup <- file.path(save_directory, "temp_PollenLookup.csv")

# import data
load(file_name_data)
lookup_fallspeed <- read.csv(file_name_fallspeed)
lookup_pollen <- read.csv(file_name_lookup)

# --- PARALLEL SETUP ---
library(parallel)

# Detect available cores and set up a cluster (leaving 1 core free for system stability)
num_cores <- max(1, detectCores() - 1)
cl <- makeCluster(num_cores)

# Export the required variables from your main environment to the parallel workers
clusterExport(cl, varlist = c("lookup_fallspeed", "lsm_unstable", "lookup_pollen"))
# ----------------------

# Run the loop in parallel using parLapply
new_columns_list <- parLapply(cl, 1:nrow(lookup_fallspeed), function(taxon) {
  
  fall_speed_class <- 100 * round(lookup_fallspeed[taxon, 2], 2) + 1 
  fall_speed_class[fall_speed_class < 2] <- 2
  
  pollen_lookup_ring <- predict(lsm_unstable[[fall_speed_class]], lookup_pollen$distance)
  ring_conversion_factor <- (0.5 / (pi * lookup_pollen$distance))
  pollen_lookup <- ring_conversion_factor * pollen_lookup_ring
  
  # Create a single-column data frame with the correct taxon name
  col_name <- paste0(lookup_fallspeed$taxon[taxon], "_DW")
  res <- data.frame(pollen_lookup)
  names(res) <- col_name
  
  return(res)
})

# Close the cluster to free up system memory
stopCluster(cl)

# Combine all parallel results side-by-side into a single data frame
new_columns_df <- do.call(cbind, new_columns_list)

# Append the new columns back to the original lookup_pollen data frame
lookup_pollen <- cbind(lookup_pollen, new_columns_df)

# Save the final output
write.csv(lookup_pollen, file.path(save_directory, "temp_PollenLookup2.csv"), row.names = FALSE)

