reshape_results <- function(results_table = acc[[2]]) {
  ntyper = ncol(results_table)/6
  
  reshaped = matrix(rep(c("reference", "optitype", "bwakit", "hlassign"), each=2), nrow = 1)
  rnames = rownames(results_table)
  
  for (row in 1:nrow(results_table)){
    
    for (i in c(1,3,5)){ #HLA-A B C
      col = sort(union(seq(i, by = 6, length.out = ntyper), seq(i+1, by = 6, length.out = ntyper)))
      #print(paste(row,col))
      reshaped = rbind(reshaped, results_table[row, col])
    }
  }
  
  colnames(reshaped) = reshaped[1,]
  reshaped = tail(reshaped, -1)
  rownames(reshaped) = rep(rnames, each=3)
  return(reshaped)
}

get_consensus <- function(reshaped_table) {
  for (i in c(3,5,7)){ #cols for typer's allele 1
    reshaped_table = cbind(reshaped_table, paste(reshaped_table[, i], reshaped_table[, i+1]))
  
  } 
  
  return(reshaped_table)
}


reshaped <- reshape_results()
consensus <- get_consensus(reshaped)